import asyncio
import logging

import datetime
import nats.aio.errors as NatsError

from edgefarm_application.base.application_module import application_module_network_nats
from edgefarm_application.base.avro import schemaless_decode

from run_task import run_task
from state_tracker import StateTracker
from schema_loader import schema_load

_logger = logging.getLogger(__name__)

_proxy_subject = "seat_info_proxy.data_timestamp"

FRESHNESS_TIMEOUT = 10


class SeatInfoProxyMonitor:
    """
    Monitor Seat Information Database proxy in cloud runtime
    """

    def __init__(self, q):
        self._q = q
        self._nc = application_module_network_nats()
        self._task = asyncio.create_task(run_task(_logger, q, self._monitor))
        self._timestamp_codec = schema_load(__file__, "timestamp")
        self._state = StateTracker(
            "Proxy-Monitor",
            {
                "UNKNOWN": "seat-info-proxy state unknown",
                "OFFLINE": "seat-info-proxy is offline",
                "OUTDATED": "seat-info-proxy data outdated",
                "FRESH": "seat-info-proxy data fresh",
            },
        )

    def stop(self):
        self._task.cancel()

    def state(self):
        return self._state.state

    async def _monitor(self):
        await self._state.update_and_send_event("UNKNOWN", self._send_event)

        while True:
            try:
                avro_response = await self._nc.request(_proxy_subject, b"", timeout=2)
                response = schemaless_decode(avro_response.data, self._timestamp_codec)
                _logger.debug(f"response from proxy {response}")

                ts = response["data"]["time"]
                now = datetime.datetime.now(datetime.timezone.utc)
                if (now - ts).total_seconds() > FRESHNESS_TIMEOUT:
                    await self._state.update_and_send_event(
                        "OUTDATED", self._send_event
                    )
                else:
                    await self._state.update_and_send_event("FRESH", self._send_event)

            except (NatsError.NatsError, NatsError.ErrTimeout):
                await self._state.update_and_send_event("OFFLINE", self._send_event)

            await asyncio.sleep(5)

    async def _send_event(self, data):
        data["train_id"] = "fleet"
        await self._q.put(data)
