import asyncio
import logging
import datetime
import nats.aio.errors as NatsError

from edgefarm_application.base.application_module import application_module_network_nats
from edgefarm_application.base.avro import schemaless_encode

from run_task import run_task
from schema_loader import schema_load

_logger = logging.getLogger(__name__)

_state_report_subject = "public.seatres.status"


class SeatResStateReporter:
    """
    Provides the status of the seat reservation system determined in the edge to
    the cloud module by periodically pushing the status on NATS subject
    "public.seatres.status" using a req/reply NATS pattern.

    The request is provided as a schemaless Avro binary using the system_status.avsc schema
    and the data fields set as follows
        - systemName:  "SeatRes"
        - status: 0=NOK, 1=OK, -1=unknown
    """

    def __init__(self, q, pis_monitor, train_id_func):
        self._pis_monitor = pis_monitor
        self._train_id_func = train_id_func
        self._nc = application_module_network_nats()
        self._task = asyncio.create_task(run_task(_logger, q, self._reporter))
        self._status_codec = schema_load(__file__, "system_status")

    def stop(self):
        self._task.cancel()

    def state(self):
        if self._pis_monitor.state_tracker_online.state is None:
            return -1
        else:
            return (
                1
                if self._pis_monitor.state_tracker_online.state is True
                and self._pis_monitor.state_tracker_seat_res_data_fresh.state  # noqa W504
                is True
                and self._pis_monitor.state_tracker_pis_errors.state  # noqa W504
                is True
                else 0
            )

    async def _reporter(self):
        while True:
            if self._train_id_func() is None:
                _logger.info("Train has no id. Don't report state to ADS")
            else:
                state = self.state()
                avro_binary = self.system_status_avro(state)
                _logger.info(f"reporting state {state}")

                try:
                    await self._nc.request(
                        _state_report_subject, avro_binary, timeout=2
                    )
                    # response message is ignored
                except (NatsError.NatsError, NatsError.ErrTimeout) as e:
                    _logger.warn(f"Can't report status to cloud module: {e}")

            await asyncio.sleep(5)

    def system_status_avro(self, state):
        msg = {
            "meta": {"version": b"\x01\x00\x00"},
            "data": {
                "time": datetime.datetime.now(),
                "trainId": self._train_id_func(),
                "systemName": "SeatRes",
                "status": state,
            },
        }
        return schemaless_encode(msg, self._status_codec)
