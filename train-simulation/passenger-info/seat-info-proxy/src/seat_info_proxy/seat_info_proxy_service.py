import asyncio
import logging

from edgefarm_application.base.application_module import application_module_network_nats
from edgefarm_application.base.avro import schemaless_decode, schemaless_encode

from schema_loader import schema_load
import cache

_logger = logging.getLogger(__name__)

_proxy_status_subject = "seat_info_proxy.data_timestamp"
_proxy_data_subject = "public.pis.seatRes"

SYNC_RATE = 5


async def run_task(logger, q, task_func):
    try:
        await task_func()
    except Exception:
        # if a task throws an exception, exit whole program
        logger.exception(f"Exception running {task_func.__name__}. Exit program")
        await q.put("stop")


class SeatInfoProxyService:
    """
    Providing Seat Reservation Informations
    """

    def __init__(self, q):
        self._nc = application_module_network_nats()
        self._q = q
        self._task = asyncio.create_task(run_task(_logger, q, self._run))
        self._timestamp_codec = schema_load(__file__, "timestamp")
        self._seat_info_request_codec = schema_load(__file__, "seat_info_request")
        self._seat_info_response_codec = schema_load(__file__, "seat_info_response")
        self._sync = 0
        self._lock = asyncio.Lock()

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
        async with self._lock:
            _logger.debug("request appinfos received")
            request = schemaless_decode(msg.data, self._seat_info_request_codec)
            trainid = request["train"]

            result = cache.get(trainid)

            # Prepare seat info data
            reservations = []
            for row in result:

                if row.startstation is not None and row.endstation is not None:
                    reservations.append(
                        {
                            "id": row.seatid,
                            "startStation": row.startstation,
                            "endStation": row.endstation,
                        }
                    )

            seat_info_response = {"seatReservations": reservations}
            await self._nc.publish(
                msg.reply,
                schemaless_encode(seat_info_response, self._seat_info_response_codec),
            )

    async def _handle_req_status(self, msg):
        _logger.debug("request status received")

        status = {
            "meta": {"version": b"\x01\x00\x00"},
            "data": {"time": self._sync},
        }
        await self._nc.publish(
            msg.reply, schemaless_encode(status, self._timestamp_codec)
        )
