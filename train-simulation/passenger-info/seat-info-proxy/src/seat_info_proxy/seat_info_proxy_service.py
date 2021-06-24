import asyncio
import logging
import datetime

from edgefarm_application.base.application_module import application_module_network_nats
from edgefarm_application.base.avro import schemaless_decode, schemaless_encode

from .run_task import run_task
from .schema_loader import schema_load
from . import cache

_logger = logging.getLogger(__name__)

_proxy_status_subject = "seat_info_proxy.data_timestamp"
_proxy_data_subject = "seat_info_proxy.data"

SYNC_RATE = 5

class SeatInfoProxyService:
    """
    Providing Seat Reservation Informations
    """

    def __init__(self):
        self._nc = application_module_network_nats()
        self._task = asyncio.create_task(self._run)
        self._timestamp_codec = schema_load(__file__, "timestamp")
        self._seat_info_request_codec = schema_load(__file__, "seat_info_request")
        self._seat_info_response_codec = schema_load(__file__, "seat_info_response")
        self._sync = 0

    def stop(self):
        self._task.cancel()

    def state(self):
        return self._state.state

    async def _run(self):
        await self._nc.subscribe(_proxy_status_subject, cb=self._handle_req_status)
        await self._nc.subscribe(_proxy_data_subject, cb=self._handle_req_data)
        while True:
            self._sync = cache.sync()
            await asyncio.sleep(SYNC_RATE)

    async def _handle_req_data(self, msg):
        _logger.debug("request appinfos received")
        request = schemaless_decode(msg, self._seat_info_request_codec)
        trainid = request["train"]
        result = cache.get(trainid)

        for row in result:
            row.trainid
            row.seatid
            row.startstation
            row.endstation


        await self._nc.publish(msg.reply, b'response')

    async def _handle_req_status(self, msg):
        _logger.debug("request status received")

        msg = {
            "meta": {"version": b"\x01\x00\x00"},
            "data": {
                "time": self._sync
            },
        }
        await self._nc.publish(msg.reply, schemaless_encode(msg, self._timestamp_codec))
