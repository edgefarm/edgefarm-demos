import logging
import datetime
import asyncio

from edgefarm_application.base.application_module import application_module_network_nats
from edgefarm_application.base.avro import schemaless_decode

from run_task import run_task
from state_tracker import StateTracker
from schema_loader import schema_load

_logger = logging.getLogger(__name__)

_state_report_subject = "public.seatres.status"


class SeatResTrainMonitor:
    def __init__(self, train_id, q):
        self.train_id = train_id
        self.edge_report_ts = None

        # this is the combined state from the train and the train online state
        self.state = StateTracker(
            "TrainSeatRes",
            {
                "UNKNOWN": "unknown",
                "OFFLINE": "offline",
                "ONLINE-UNKNOWN": "online, unclear state",
                "ONLINE-NOK": "online, but not ok",
                "ONLINE-OK": "online, ok",
            },
        )
        # this is just the online state of the train
        self.state_online = StateTracker(
            "Train-Online-Monitor",
            {
                "UNKNOWN": "train state unknown",
                "OFFLINE": "train is offline",
                "ONLINE": "train is online",
            },
        )
        self._q = q
        self._task = asyncio.create_task(run_task(_logger, q, self._watchdog))

    async def start(self):
        self.state.update("UNKNOWN")
        await self.state_online.update_and_send_event("UNKNOWN", self._send_event)

    def stop(self):
        self._task.cancel()

    async def update_edge_state(self, state):
        self.edge_report_ts = datetime.datetime.now()

        if state == -1:
            up_state = "ONLINE-UNKNOWN"
        elif state == 0:
            up_state = "ONLINE-NOK"
        elif state == 1:
            up_state = "ONLINE-OK"

        self.state.update(up_state)
        await self.state_online.update_and_send_event("ONLINE", self._send_event)

    async def _watchdog(self):
        while True:
            now = datetime.datetime.now()

            if self.edge_report_ts is not None:
                if (now - self.edge_report_ts).total_seconds() > 10:
                    self.state.update("OFFLINE")
                    await self.state_online.update_and_send_event(
                        "OFFLINE", self._send_event
                    )

            await asyncio.sleep(1)

    async def _send_event(self, data):
        data["train_id"] = self.train_id
        await self._q.put(data)


class TrainStatusCollector:
    """
    Collect seat reservation system status of all trains.

    The individual trains report their SeatRes state via Nats subject 'public.seatres.status' to
    this module.
    """

    def __init__(self, q):
        self._nc = application_module_network_nats()
        self._q = q
        self._state_report_codec = schema_load(__file__, "system_status")
        self._trains = {}

    async def start(self):
        self._state_report_subscription_id = await self._nc.subscribe(
            _state_report_subject, cb=self._state_report_handler
        )

    async def stop(self):
        await self._nc.unsubscribe(self._state_report_subscription_id)
        for v in self._trains.values():
            v.stop()

    async def add_train(self, train_id):
        if train_id not in self._trains.keys():
            v = SeatResTrainMonitor(train_id, self._q)
            self._trains[train_id] = v
            await v.start()
        else:
            v = self._trains[train_id]
        return v

    def trains(self):
        return self._trains.values()

    async def _state_report_handler(self, nats_msg):
        """
        Called when a NATS message is received on _state_report_subject
        """
        reply_subject = nats_msg.reply
        msg = schemaless_decode(nats_msg.data, self._state_report_codec)
        _logger.debug(f"state report received msg {msg}")

        train_id = msg["data"]["trainId"]
        try:
            v = self._trains[train_id]
            await self._update_edge_state(v, msg)
        except KeyError:
            _logger.info(f"received state report from new train {train_id}")
            v = await self.add_train(train_id)
            await self._update_edge_state(v, msg)

        await self._nc.publish(reply_subject, b"")

    async def _update_edge_state(self, v, msg):
        try:
            await v.update_edge_state(msg["data"]["status"])
        except KeyError:
            _logger.error(f"couldn't find [data][status] in {msg}")
