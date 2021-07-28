import asyncio
import datetime
import time
import logging
from run_task import run_task

_logger = logging.getLogger(__name__)

FRESHNESS_TIMEOUT = 10.0


class StateTracker:
    def __init__(self, name, state_messages: dict):
        self.name = name
        self.state = None
        self._update_called = False
        self._state_messages = state_messages

    def update(self, new_state):
        msg = None
        new_state_str = str(new_state)

        if new_state != self.state or not self._update_called:
            msg = self._state_messages[new_state_str]
            self.state = new_state

        self._update_called = True
        return msg

    async def update_and_send_event(self, new_state, send_func):
        msg = self.update(new_state)
        if msg is not None:
            await send_func(
                {"time": datetime.datetime.now(), "source": self.name, "event": msg}
            )
        return msg


class PisMonitor:
    def __init__(self, q, mqtt_client):
        self._name = "PIS"
        self._q = q
        self._mqtt_client = mqtt_client
        self._tasks = []

        self.state_tracker_online = StateTracker(
            "PIS-Online-Monitor",
            {
                "None": "PIS state unknown",
                "False": "PIS offline",
                "True": "PIS online",
            },
        )

        self.state_tracker_pis_errors = StateTracker(
            "PIS-Error-Monitor",
            {
                "None": "PIS errors unknown",
                "False": "PIS reported internal error",
                "True": "PIS reported no internal error",
            },
        )

        self.state_tracker_seat_res_data_fresh = StateTracker(
            "PIS-SeatResv-Freshness-Monitor",
            {
                "None": "seat info data freshnesss unknown",
                "False": "seat info data outdated",
                "True": "seat info data fresh",
            },
        )

        for task_func in [
            self._monitor_online,
            self._monitor_error,
            self._monitor_seatres_fresh,
        ]:
            self._tasks.append(
                asyncio.create_task(run_task(_logger, self._q, task_func))
            )

    def stop(self):
        for task in self._tasks:
            task.cancel()

    async def _monitor_online(self):
        """
        Periodically check if PIS is reachable (online)
        """
        state_tracker = self.state_tracker_online
        await state_tracker.update_and_send_event(None, self._send_event)

        seq_no = 0
        while True:
            seq_no += 1
            state = False
            ping_msg = f"ping: {seq_no}".encode()
            error, response = await self.pis_query("pis/cmd/state", ping_msg)
            if not error and response == ping_msg:
                state = True

            await state_tracker.update_and_send_event(state, self._send_event)

            await asyncio.sleep(3.0)

    async def _monitor_error(self):
        """
        Periodically check if PIS has internal errors
        """
        state_tracker = self.state_tracker_pis_errors
        await state_tracker.update_and_send_event(None, self._send_event)

        while True:
            error, response = await self.pis_query("pis/cmd/error_state", b"")

            # update error state only if PIS answers
            if not error:
                state = response == b"false"
                await state_tracker.update_and_send_event(state, self._send_event)

            await asyncio.sleep(2.0)

    async def _monitor_seatres_fresh(self):
        """
        Periodically check if PIS has fresh seat reservation data
        """
        state_tracker = self.state_tracker_seat_res_data_fresh
        await state_tracker.update_and_send_event(None, self._send_event)
        old_last_sr_upadate = last_sr_update = 0  # seconds since epoch

        while True:
            error, response = await self.pis_query("pis/cmd/seatres_update_time", b"")

            if not error:
                last_sr_update = int(response) / 1000.0

                if last_sr_update != old_last_sr_upadate:
                    await self._send_event(
                        {
                            "time": datetime.datetime.fromtimestamp(last_sr_update),
                            "source": "PIS-SeatResData",
                            "event": "Seatres. data updated",
                        }
                    )
                    old_last_sr_upadate = last_sr_update

            age = time.time() - last_sr_update
            if last_sr_update != 0:
                state = age < FRESHNESS_TIMEOUT
                await state_tracker.update_and_send_event(state, self._send_event)

            await asyncio.sleep(1.0)

    async def pis_query(self, topic, req_data):
        error = False
        response = None
        try:
            _logger.debug(f"query {topic}")
            response = await self._mqtt_client.request(topic, req_data, timeout=3000)
        except RuntimeError:
            error = True

        return error, response

    async def _send_event(self, data):
        await self._q.put(data)
