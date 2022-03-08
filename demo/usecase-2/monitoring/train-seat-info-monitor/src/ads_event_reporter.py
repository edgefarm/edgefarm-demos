import logging

import edgefarm_application as ef
from schema_loader import schema_read

_logger = logging.getLogger(__name__)


class AdsEventReporter:
    """
    Forwards system events to ADS.
    """

    def __init__(self, train_id_func):
        self._ads_producer = ef.AdsProducer()
        self._train_id_func = train_id_func

        # Create an encoder for an application specific payload
        payload_schema = schema_read(__file__, "system_event")
        self._ads_encoder = ef.AdsEncoder(
            payload_schema,
            schema_name="system_event",
            schema_version=(1, 0, 0),
            tags={},
        )

    async def report(self, event):
        if self._train_id_func() is None:
            _logger.info("Train has no id. Don't report event to ADS")
            return

        ads_payload = {
            "data": {
                "time": event["time"],
                "trainId": self._train_id_func(),
                "source": event["source"],
                "event": event["event"],
            },
        }
        _logger.debug(f"sending event to ADS: {ads_payload}")
        # Send data to ads node module
        await self._ads_producer.encode_and_send(self._ads_encoder, ads_payload)
