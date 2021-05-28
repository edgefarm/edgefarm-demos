import io
import os
import signal
import asyncio
import datetime
from nats.aio.client import Client as Nats
import edgefarm.avro as avro
from edgefarm.ads import AdsProducer, AdsEncoder

#
# Using ads_client, you can publish a message towards ADS
#
ads_client = None
ads_encoder = None


async def gps_handler(msg):
    """This is the handler function that is called whenever a new GPS dataset arrives`.
    The received data is encoded using `Apache avro` with the schema defined in
    "https://github.com/edgefarm/alm-service-modules/blob/main/alm-location-module/main.go"

    This example unpacks the original message and encodes it into an ADS_DATA avro message (see `edgefarm/ads_schemas/ads_data.avsc`).
    The payload in ADS_DATA is another AVRO message with a schema for a temperature sensor (see `edgefarm/ads_schemas/gps_data.avsc`)
    The whole ADS_DATA message is then sent to ads-node module.
    """
    message = avro.schema_decode(io.BytesIO(msg.data))

    print(message)
    org_payload = message

    # Generate an ADS payload with "temperature_data" schema
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
    ads_data_binary = ads_encoder.encode(
        tags=[{"key": "mon", "value": "true"}],
        payload_schema="gps_data",
        schema_version=b"\x01\x00\x00",
        data=ads_payload,
    )
    # Send data to ads node module
    await ads_client.publish(ads_data_binary)


async def main():
    loop = asyncio.get_event_loop()
    global ads_client, ads_encoder

    #
    # Connect to NATS and subscribe to "service.location" subject
    #
    nc = Nats()
    nats_server = os.getenv("NATS_SERVER", "nats:4222")
    await nc.connect(servers="nats://" + nats_server, loop=loop)
    print("NATS connect ok")
    subscription_id = await nc.subscribe("service.location", cb=gps_handler)

    # Connect to NATS to publish to "ads" subject which is consumed by ADS Node module
    ads_client = AdsProducer(loop)
    await ads_client.connect()

    # Instantiate an ADS DATA encoder to produce the ADS avro message
    # Register the embedded data schemas (here: temperature data)
    # If you need further schemas, add them to the list of <payload_schemas>

    device_id = os.getenv("IOTEDGE_DEVICEID", "no-device-id")
    ads_encoder = AdsEncoder(
        app="GPS", module=f"{device_id}.gps", payload_schemas=["gps_data"]
    )

    stop = {"stop": False}

    #
    # The following shuts down gracefully when SIGINT or SIGTERM is received
    #
    def signal_handler():
        stop["stop"] = True

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    while not stop["stop"]:
        await asyncio.sleep(1)

    print("Unsubscribing and shutting down...")
    await nc.unsubscribe(subscription_id)
    await nc.close()
    await ads_client.close()


if __name__ == "__main__":
    asyncio.run(main())
