import asyncio
import datetime
import logging
from run_task import run_task

_logger = logging.getLogger(__name__)


class TrainIdProvider:
    def __init__(self, q, mqtt_client):
        self._q = q
        self._mqtt_client = mqtt_client
        self._task = asyncio.create_task(run_task(_logger, self._q, self._monitor))
        self._train_id = None

    def stop(self):
        for task in self._tasks:
            task.cancel()

    def train_id(self):
        return self._train_id

    async def _monitor(self):
        """
        Periodically check for train Id changes
        """
        while True:
            error, response = await self._query("tcms/cmd/trainid", b"")

            if not error:
                train_id = response.decode()
                if train_id != "" and train_id != self._train_id:
                    self._train_id = train_id
                    await self._send_event(
                        {
                            "time": datetime.datetime.now(),
                            "source": "TCMS",
                            "event": f"new train id {train_id}",
                        }
                    )

            await asyncio.sleep(3.0)

    async def _query(self, topic, req_data):
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
