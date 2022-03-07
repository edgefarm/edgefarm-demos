import logging

import edgefarm_application as ef
from schema_loader import schema_read

_logger = logging.getLogger(__name__)


class AdsEventReporter:
    """
    Forwards detected peaks to ADS.
    """

    def __init__(self):
        self._ads_producer = ef.AdsProducer()

        # Create an encoder for an application specific payload
        payload_schema = schema_read(__file__, "vibration_intensity")
        self._ads_encoder = ef.AdsEncoder(
            payload_schema,
            schema_name="vibration_intensity",
            schema_version=(1, 0, 0),
            tags={},
        )

    async def report(self, event):
        ads_payload = {"data": event}
        _logger.debug(f"sending event to ADS: {ads_payload}")
        # Send data to ads node module
        await self._ads_producer.encode_and_send(self._ads_encoder, ads_payload)
