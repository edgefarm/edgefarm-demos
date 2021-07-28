import datetime


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
