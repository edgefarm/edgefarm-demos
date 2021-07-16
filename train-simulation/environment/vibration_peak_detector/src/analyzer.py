import asyncio
import numpy as np
import json
import logging
import datetime
import math

from fifo import Fifo
from run_task import run_task
import location_mapper

ACCEL_FIFO_CAPACITY = 6000  # number of samples in Acceleration Data Fifo ~1 minute
ACCEL_NOMINAL_SAMPLE_PERIOD = 0.01  # sample rate we except the samples to arrive
LOC_FIFO_CAPACITY = 60  # number of samples in Location Fifo
RMS_WINDOW_SIZE = 80  # number of samples over which RMS is computed
PEAK_THRESHOLD = 0.42  # if RMS value above that threshold, send ADS message
MAP_TIMESTAMP_TIMEOUT_SECONDS = 60


_logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, q, mqtt_client):
        self._q = q
        self._mqtt_client = mqtt_client
        self._logic = AnalyzerLogic(
            RMS_WINDOW_SIZE, ACCEL_NOMINAL_SAMPLE_PERIOD)
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
        _logger.debug(
            f"Place {n} accel samples into fifo. age={age.total_seconds()} s")

        # Push into Fifo
        try:
            self._accel_fifo.push(arr)
            await self._accel_q.put(0)
        except BufferError as e:
            _logger.error(f"Accel Fifo: {e}")

    async def _loc_handler(self, msg):
        """This is the handler function that gets registered for `environment/location`"""
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
                    _logger.debug(
                        f"Got {RMS_WINDOW_SIZE} accel samples from fifo.")

                    ts, rms = self._logic.analyze(accel)

                    if ts is not None:
                        map_status, lat, lon = await self.map_timestamp(ts)
                        _logger.info(f"RMS={rms} at ts={ts} loc={lat}, {lon}")

                        # Discard location entries that are too old
                        self.clean_locs_fifo(ts)

                        if map_status == "ok" and rms > PEAK_THRESHOLD:
                            # report peak to main task
                            _logger.info("*** Peak detected!")

                            await self._q.put(
                                {
                                    "time": datetime.datetime.fromtimestamp(float(ts)),
                                    "lat": lat,
                                    "lon": lon,
                                    "vibrationIntensity": rms,
                                }
                            )

                except BufferError:
                    # not enough data in fifo, wait for more
                    break

    async def map_timestamp(self, ts):
        """
        Map the timestamp to a location position.
        If ts is newer than all received locations, wait for newer locations

        :param ts: timestamp to map
        :return: map_status, lat, lon
                  "ok" - mapping done - lat, lon valid
                  "ts-too-old" mapping failed - ts is older than all timestamps in locs
                  "time-gap" mapping failed - time gap in accel
        """
        if ts is None:
            map_status = "time-gap"
            lat = lon = None
        else:
            elapsed_time_seconds = 0
            while elapsed_time_seconds < MAP_TIMESTAMP_TIMEOUT_SECONDS:
                locs = self._loc_fifo.peek(self._loc_fifo.entries())
                lat, lon, map_status = location_mapper.map_timestamp_to_location(
                    ts, locs
                )

                if map_status == "ts-too-new":
                    # no location data available. Let's wait
                    _logger.info("Wait for newer location data")
                    await asyncio.sleep(1)
                    elapsed_time_seconds += elapsed_time_seconds
                else:
                    break

        if map_status != "ok":
            _logger.warn(f"Could not map timestamp to location: {map_status}")

        return map_status, lat, lon

    def clean_locs_fifo(self, ts):
        locs = self._loc_fifo.peek(self._loc_fifo.entries())
        unused_loc_idx = location_mapper.find_last_unused_location_entry(
            ts, locs)
        if unused_loc_idx is not None:
            self._loc_fifo.pop(unused_loc_idx + 1)


class AnalyzerLogic:
    def __init__(self, rms_window_size, accel_nominal_sample_period):
        """
        Stateless logic of Analyzer
        """
        self._rms_window_size = rms_window_size
        self._accel_nominal_sample_period = accel_nominal_sample_period

    def analyze(self, accel):
        """
        Determine RMS value of <accel>.

        :param accel: chunk of RMS_WINDOW_SIZE z-acceleration samples
        :return: ts, rms

        <ts> timestamp of middle entry of accel - none if accel data has time gaps
        <rms> rms value of accel
        """
        rms = None
        ts = None

        # ensure all data in the buffer is from the "same" moment
        if self._has_time_gaps(accel):
            _logger.error("Time gap. Not analyzing data")
        else:
            # Compute RMS value
            rms = self._analyze_chunk(accel)

            # Get timestamp in the middle of the window
            ts = accel[int(len(accel) / 2), 0]

        return ts, rms

    @staticmethod
    def _analyze_chunk(accel):
        """
        Build the RMS over differential over the z-acceleration
        :return: rms
        """
        # compute differential
        d_accel = np.ndarray((len(accel)))
        d_accel = np.diff(accel[:, 1], prepend=accel[0, 1])

        # compute RMS value over differential
        rms = AnalyzerLogic._calculate_rms(d_accel)
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

        :return: lat, lon, status
        <lat>, <lon>: averaged position at time (linear interpolation)
        <status>: "ok" - mapping done
                  "ts-too-new" ts is newer than all timestamps in locs, or locs is empty
                  "ts-too-old" ts is older than all timestamps in locs
        """
        status = "ts-too-old" if len(locs) > 0 else "ts-too-new"
        for idx in range(len(locs)):
            try:
                if ts >= locs[idx, 0] and ts < locs[idx + 1, 0]:
                    td = ts - locs[idx, 0]
                    f = td / (locs[idx + 1, 0] - locs[idx, 0])
                    lat = (locs[idx + 1, 1] - locs[idx, 1]) * f + locs[idx, 1]
                    lon = (locs[idx + 1, 2] - locs[idx, 2]) * f + locs[idx, 2]

                    return lat, lon, "ok"
            except IndexError:
                status = "ts-too-new"
                break

        if len(locs > 0):
            _logger.error(f"oldest: {ts-locs[0,0]} newest: {ts-locs[-1,0]}")
        return None, None, status

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
