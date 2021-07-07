import asyncio
import numpy as np
import json
import logging
import datetime
import math
import time

from fifo import Fifo
from run_task import run_task

ACCEL_FIFO_CAPACITY = 600
ACCEL_NOMINAL_SAMPLE_PERIOD = 0.01  # sample rate we except the samples to arrive
LOC_FIFO_CAPACITY = 20
RMS_WINDOW_SIZE = 80
PEAK_THRESHOLD = 0.42

_logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, q, mqtt_client):
        self._mqtt_client = mqtt_client
        self._logic = AnalyzerLogic(
            RMS_WINDOW_SIZE, ACCEL_NOMINAL_SAMPLE_PERIOD, PEAK_THRESHOLD
        )
        # communication between accel_handler and monitor task
        self._accel_fifo = Fifo((ACCEL_FIFO_CAPACITY, 2))
        self._accel_q = asyncio.Queue()

        self._loc_fifo = Fifo((LOC_FIFO_CAPACITY, 3))

        self._task = asyncio.create_task(run_task(_logger, q, self._monitor))

    async def _accel_handler(self, msg):
        """This is the handler function that gets registered for `environment/acceleration`.
        The received data is a python dictionary.
        msg['payload'] is the MQTT message as received from MQTT. Here, the payload is
        a json message, so we convert the json to a python dictionary.
        """
        t1 = time.perf_counter()
        payload = json.loads(msg["payload"])

        # Z-acceleration + timestamps to np-array
        accel = payload["accel"]
        n = len(accel)
        ts = payload["time"]
        td = payload["time_delta"]
        arr = np.ndarray((n, 2))

        for i in range(n):
            arr[i, 0] = ts + td * i
            arr[i, 1] = accel[i]["z"]

        age = datetime.datetime.now() - datetime.datetime.fromtimestamp(float(ts))
        _logger.debug(f"Place {n} accel samples into fifo. age={age.total_seconds()} s")

        # Push into Fifo
        try:
            self._accel_fifo.push(arr)
            await self._accel_q.put(0)
        except BufferError as e:
            _logger.error(f"Accel Fifo: {e}")

        _logger.debug(f"accel_handler: {time.perf_counter()-t1}")

    async def _loc_handler(self, msg):
        payload = json.loads(msg["payload"])
        _logger.debug(f"loc_handler {payload}")
        try:
            entry = np.array([payload["time"], payload["lat"], payload["lon"]])
            self._loc_fifo.push(entry)
        except BufferError as e:
            _logger.error(f"Loc Fifo: {e}")

    async def register_handlers(self):
        await self._mqtt_client.subscribe(
            "environment/acceleration", self._accel_handler
        )
        await self._mqtt_client.subscribe("environment/location", self._loc_handler)

    async def _monitor(self):
        await self.register_handlers()

        while True:
            # wait for accel_handler to put something into FIFO
            await self._accel_q.get()
            while True:
                try:
                    accel = self._accel_fifo.pop(RMS_WINDOW_SIZE)
                    _logger.debug(f"Got {RMS_WINDOW_SIZE} accel samples from fifo.")

                    locs = self._loc_fifo.peek(self._loc_fifo.entries())

                    peak_value, ts, lat, lon, unused_loc_idx = self._logic.main(
                        accel, locs
                    )
                    _logger.info(
                        f"Peakvalue={peak_value} ts={ts} lat={lat} lon={lon} unused_loc_idx={unused_loc_idx}"
                    )

                    # Discard location entries that are too old
                    if unused_loc_idx is not None:
                        self._loc_fifo.pop(unused_loc_idx + 1)

                except BufferError:
                    # not enough data in fifo, wait for more
                    break


class AnalyzerLogic:
    def __init__(self, rms_window_size, accel_nominal_sample_period, peak_threshold):
        """
        Stateless logic of Analyzer
        """
        self._rms_window_size = rms_window_size
        self._accel_nominal_sample_period = accel_nominal_sample_period
        self._peak_threshold = peak_threshold

    def main(self, accel, locs):
        """
        Determine if the <accel> data's RMS value is over <peak_threshold>.
        Map the accel data to a location position (correlated by timestamps).

        :param accel: chunk of RMS_WINDOW_SIZE z-acceleration samples
        :param location: Location data records
        :return: peak_value, ts, lat, lon, unused_loc_idx

        <peak_value> If peak detected, rms of peak else None
        <ts> timestamp of middle entry of accel
        <lat>,<lon> location at <ts>. None if it can't be mapped
        <unused_loc_idx>: last location entry that is no more used. Can be None
        """
        peak_value = None
        lat = None
        lon = None
        unused_loc_idx = None

        # ensure all data in the buffer is from the "same" moment
        if self._has_time_gaps(accel):
            _logger.error("Time gap. Not analyzing data")
        else:
            # Compute RMS value
            rms = self._analyze_chunk(accel)

            # Get timestamp in the middle of the window
            ts = accel[int(len(accel) / 2), 0]
            _logger.debug(f"RMS at {ts}: {rms}")

            if rms > self._peak_threshold:
                peak_value = rms

            try:
                lat, lon = self._map_timestamp_to_location(ts, locs)
            except LookupError as e:
                _logger.error(f"Could not map timestamp to location: {e}")

            unused_loc_idx = self._find_last_unused_location_entry(ts, locs)

        return peak_value, ts, lat, lon, unused_loc_idx

    @staticmethod
    def _analyze_chunk(accel):
        """
        Build the RMS over differential over the z-acceleration
        :return: rms
        """

        t1 = time.perf_counter()

        # compute differential
        accel[:, 1] = np.diff(accel[:, 1], prepend=accel[0, 1])

        # compute RMS value over differential
        rms = AnalyzerLogic._calculate_rms(accel[:, 1])

        _logger.debug(f"analyze_window: {time.perf_counter()-t1}")
        return rms

    @staticmethod
    def _calculate_rms(chunk):
        chunk = pow(abs(chunk), 2)
        return math.sqrt(chunk.mean())

    def _has_time_gaps(self, accel):
        dt = accel[-1, 0] - accel[0, 0]
        _logger.debug(f"time_gap={dt}")
        return dt > (self._accel_nominal_sample_period * self._rms_window_size * 1.1)

    @staticmethod
    def _map_timestamp_to_location(ts, locs):
        """
        Find the location (lat,lon) at time <ts> in <locs>.
        <locs> must be array with entries [time,lat,lon], oldest entry first

        :return: lat, lon
        <lat>, <lon>: averaged position at time (linear interpolation)

        :raise LookupError: if ts can't be mapped to a location
        """
        for idx in range(len(locs)):
            try:
                if ts >= locs[idx, 0] and ts < locs[idx + 1, 0]:
                    td = ts - locs[idx, 0]
                    f = td / (locs[idx + 1, 0] - locs[idx, 0])
                    lat = (locs[idx + 1, 1] - locs[idx, 1]) * f + locs[idx, 1]
                    lon = (locs[idx + 1, 2] - locs[idx, 2]) * f + locs[idx, 2]

                    return lat, lon
            except IndexError:
                break

        if len(locs > 0):
            _logger.error(f"oldest: {ts-locs[0,0]} newest: {ts-locs[-1,0]}")
        raise (LookupError(f"ts {ts} can't be found. {len(locs)} entries present."))

    @staticmethod
    def _find_last_unused_location_entry(ts, locs):
        """
        Find the last location entry that is no more used.
        i.e. the last entry that is older than the one just before <ts>.
        <locs> must be array with entries [time,lat,lon], oldest entry first

        :return: idx or None
        """
        idx = 0
        for idx in range(len(locs)):
            try:
                if ts >= locs[idx, 0] and ts < locs[idx + 1, 0]:
                    break
            except IndexError:
                break
        if idx > 0:
            return idx - 1
