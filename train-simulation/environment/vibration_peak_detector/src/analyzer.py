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
RMS_WINDOW_SIZE = 80
PEAK_THRESHOLD = 0.42

_logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, q, mqtt_client):
        self._mqtt_client = mqtt_client
        self._accel_fifo = Fifo((ACCEL_FIFO_CAPACITY, 2))
        self._accel_q = (
            asyncio.Queue()
        )  # communication between accel_handler and monitor task
        self._task = asyncio.create_task(run_task(_logger, q, self._monitor))

    async def accel_handler(self, msg):
        """This is the handler function that gets registered for `environment/acceleration`.
        The received data is a python dictionary.
        msg['payload'] is the MQTT message as received from MQTT. Here, the payload is
        a json message, so we convert the json to a python dictionary.
        """
        t1 = time.perf_counter()
        payload = json.loads(msg["payload"])
        # print(f"{msg}: payload={payload}")

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
        _logger.info(f"Place {n} accel samples into fifo. age={age.total_seconds()} s")

        # Push into Fifo
        try:
            self._accel_fifo.push(arr)
            await self._accel_q.put(0)
        except BufferError as e:
            _logger.warn(e)

        _logger.debug(f"accel_handler: {time.perf_counter()-t1}")

    async def register_handlers(self):
        await self._mqtt_client.subscribe(
            "environment/acceleration", self.accel_handler
        )

    async def _monitor(self):
        await self.register_handlers()

        while True:
            await self._accel_q.get()
            while True:
                try:
                    accel = self._accel_fifo.pop(RMS_WINDOW_SIZE)
                    self._peak_detect(accel)
                    _logger.info(f"Got {RMS_WINDOW_SIZE} accel samples from fifo.")

                except BufferError:
                    # not enough data in fifo, wait for more
                    break

    def _peak_detect(self, accel):
        t1 = time.perf_counter()

        # ensure all data in the buffer is from the "same" moment
        if self._has_time_gaps(accel):
            _logger.warn("Time gap. Not analyzing data")
            return

        # differentiate to get rid of bias
        accel[:, 1] = np.diff(accel[:, 1], prepend=accel[0, 1])

        # compute RMS value of window
        rms = self._calculate_rms(accel[:, 1])

        # Get timestamp in the middle of the window
        ts = accel[int(len(accel) / 2), 0]
        _logger.info(f"RMS at {ts}: {rms}")

        if rms > PEAK_THRESHOLD:
            _logger.info(f"DETECT PEAK at {ts}: {rms}")

        _logger.debug(f"peak_detect: {time.perf_counter()-t1}")

    def _calculate_rms(self, chunk):
        chunk = pow(abs(chunk), 2)
        return math.sqrt(chunk.mean())

    def _has_time_gaps(self, accel):
        dt = accel[-1, 0] - accel[0, 0]
        _logger.debug(f"time_gap={dt}")
        return dt > (ACCEL_NOMINAL_SAMPLE_PERIOD * RMS_WINDOW_SIZE * 1.1)
