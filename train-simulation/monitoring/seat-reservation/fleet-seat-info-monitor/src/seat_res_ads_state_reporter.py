import asyncio
import logging
import datetime

import edgefarm_application as ef

from run_task import run_task
from schema_loader import schema_read

_logger = logging.getLogger(__name__)


class SeatResAdsStateReporter:
    """
    Provides the status of the seat reservation system per train to ADS.

    For each train, a separate ADS message is sent.
    ADS messages are produced periodically.

    :param q: event q to place occurred events
    :param trains_func: function returning list of train objects
    :param seat_info_proxy_status_func: function to provide status of seat_info_proxy
    """

    def __init__(self, q, trains_func, seat_info_proxy_status_func):
        self._trains_func = trains_func
        self._seat_info_proxy_status_func = seat_info_proxy_status_func
        self._task = asyncio.create_task(run_task(_logger, q, self._reporter))
        self._ads_producer = ef.AdsProducer()

        # Create an encoder for an application specific payload
        payload_schema = schema_read(__file__, "system_status")
        self._ads_encoder = ef.AdsEncoder(
            payload_schema,
            schema_name="system_status",
            schema_version=(1, 0, 0),
            tags={},
        )

    def stop(self):
        self._task.cancel()

    def state(self, train_state, cloudmod_state):
        if train_state == "ONLINE-OK":
            return 1
        else:
            return 0
        # TODO: consider cloudmod_state

    async def _reporter(self):
        while True:
            for t in self._trains_func():
                await self._report_train(t)
            await asyncio.sleep(5)

    async def _report_train(self, t):
        state = self.state(t.state.state, None)
        _logger.info(f"reporting state for {t.train_id}: {state}")

        ads_payload = {
            "data": {
                "time": datetime.datetime.now(),
                "trainId": t.train_id,
                "systemName": "SeatRes",
                "status": state,
            },
        }
        # Send data to ads node module
        await self._ads_producer.encode_and_send(self._ads_encoder, ads_payload)
