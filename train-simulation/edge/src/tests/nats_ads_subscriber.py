import os
from nats.aio.client import Client as Nats
from io import BytesIO
import asyncio
import fastavro


async def run(loop):
    nc = Nats()

    nats_server = os.getenv("NATS_SERVER", "nats:4222")
    ads_codec = fastavro.schema.load_schema(
        os.path.join("../edgefarm/ads-schemas", "ads_data.avsc")
    )

    await nc.connect(servers="nats://" + nats_server, loop=loop)
    print("nc.connect ok")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        ads_data = avro_deserialize(msg.data, ads_codec)
        data = decode_payload(ads_data["payload"])
        print(f"Received a message on '{subject} {reply}': {ads_data}\n{data}")

    # Simple publisher and async subscriber via coroutine.
    await nc.subscribe("ads", cb=message_handler)


def decode_payload(payload):
    codec = fastavro.schema.load_schema(
        os.path.join("../edgefarm/ads-schemas", payload["schema"])
    )
    return avro_deserialize(payload["data"], codec)


def avro_deserialize(data, schema):
    fo = BytesIO(data)
    m = fastavro.schemaless_reader(fo, schema)
    return m


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
    loop.close()
