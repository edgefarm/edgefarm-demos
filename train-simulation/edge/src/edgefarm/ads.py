import os
from nats.aio.client import Client as Nats
import fastavro
from .avro import schemaless_encode


class AdsProducer:
    def __init__(self, loop):
        self.nc = Nats()
        self.loop = loop
        self.serverRunning = False

    async def connect(self):
        """Connect to the nats server.
        You can specify the nats server by defining the environment
        variable `NATS_SERVER`, e.g. `nats:4222`.
        """
        nats_server = os.getenv("NATS_SERVER", "nats:4222")
        options = {
            "servers": ["nats://" + nats_server],
            "loop": self.loop,
            "connect_timeout": 10,
            "ping_interval": 1,
            "max_outstanding_pings": 5,
        }

        await self.nc.connect(**options)

    async def publish(self, data):
        await self.nc.publish("ads", data)

    async def close(self):
        if self.nc.is_closed:
            return
        try:
            await self.nc.close()
        except Exception as e:
            print(e)


class AdsEncoder:
    def __init__(self, app, module, payload_schemas):
        self.codec = fastavro.schema.load_schema("edgefarm/ads-schemas/ads_data.avsc")
        self.payload_codecs = {}
        self.app = app
        self.module = module
        self.sequence_number = 0
        for f in payload_schemas:
            self.payload_codecs[f] = fastavro.schema.load_schema(
                f"edgefarm/ads-schemas/{f}.avsc"
            )

    def encode(self, tags, payload_schema, schema_version, data):
        """
        Generate an ADS_DATA avro (schemaless) message with an embedded avro payload of using the <payload_schema>.
        <payload_schema> must have been specified when initializing this component
        """

        if payload_schema not in self.payload_codecs.keys():
            raise ValueError(f"schema {payload_schema} unknown")

        # encode payload
        payload = schemaless_encode(data, self.payload_codecs[payload_schema])

        # encode ADS_DATA
        msg = {
            "meta": {"version": b"\x01\x00\x00"},
            "origin": {
                "app": self.app,
                "module": self.module,
                "tags": tags,
                "sequenceNumber": self.sequence_number,
            },
            "payload": {
                "format": "avro",
                "schema": payload_schema + ".avsc",
                "schemaVersion": schema_version,
                "data": payload,
            },
        }
        avro_msg = schemaless_encode(msg, self.codec)
        self.sequence_number += 1
        return avro_msg
