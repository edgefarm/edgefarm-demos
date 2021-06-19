import os
import signal
import asyncio
import datetime
from nats.aio.client import Client as Nats

import edgefarm_application as ef
from edgefarm_application.base.schema import schema_read_builtin
from edgefarm_application.base.avro import schema_decode


#
# Using the ads_producer/encoder, you can publish a message towards ADS
#
ads_producer = None
ads_encoder = None


async def gps_handler(msg):
    """This is the NATS handler function that is called whenever a new GPS dataset arrives`.
    The received data is encoded using `Apache avro` with the schema defined in
    "https://github.com/edgefarm/alm-service-modules/blob/main/alm-location-module/main.go"

    This example unpacks the original message and encodes it into an ADS_DATA avro message.
    The payload in ADS_DATA is an AVRO message with a schema for GPS (see `schemas/gps_data.avsc`)
    The whole ADS_DATA message is then sent to ads-node module.
    """
    org_payload = schema_decode(msg.data)

    print(org_payload)

    # Generate an ADS payload with "gps_data" schema
    ads_payload = {
        "meta": {"version": b"\x01\x00\x00"},
        "data": {
            "time": datetime.datetime.fromtimestamp(int(org_payload["acqTime"])),
            "lat": float(org_payload["lat"]),
            "lon": float(org_payload["lon"]),
            "alt": 0.0,
            "gpsMode": int(org_payload["mode"]),
        },
    }
    # Send data to ads node module
    await ads_producer.encode_and_send(ads_encoder, ads_payload)


async def main():
    global ads_producer, ads_encoder
    loop = asyncio.get_event_loop()

    # Initialize EdgeFarm SDK
    if os.getenv("IOTEDGE_MODULEID") is not None:
        await ef.application_module_init_from_environment(loop)
    else:
        print("Warning: Running example outside IOTEDGE environment")
        await ef.application_module_init(loop, "", "", "")

    ads_producer = ef.AdsProducer()

    # Create the encoder for an application specific payload
    payload_schema = schema_read_builtin(__file__, "schemas/gps_data.avsc")
    ads_encoder = ef.AdsEncoder(
        payload_schema,
        schema_name="gps_data",
        schema_version=(1, 0, 0),
        tags={"monitor": "channel1"},
    )

    #
    # Connect to NATS and subscribe to "service.location" subject
    #
    nc = Nats()
    nats_server = os.getenv("NATS_SERVER", "nats:4222")
    await nc.connect(servers="nats://" + nats_server, loop=loop)
    print("NATS connect ok")
    subscription_id = await nc.subscribe("service.location", cb=gps_handler)

    #
    # The following shuts down gracefully when SIGINT or SIGTERM is received
    #
    stop = {"stop": False}

    def signal_handler():
        stop["stop"] = True

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    while not stop["stop"]:
        await asyncio.sleep(1)

    print("Unsubscribing and shutting down...")
    await nc.unsubscribe(subscription_id)
    await nc.close()
    await ef.application_module_term()


if __name__ == "__main__":
    asyncio.run(main())
