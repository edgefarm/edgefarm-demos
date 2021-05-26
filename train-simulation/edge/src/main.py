import io
import os
import signal
import sys
import asyncio
import datetime
import json
import edgefarm.avro as avro
from edgefarm.alm_mqtt_module_client import AlmMqttModuleClient
from edgefarm.ads import AdsProducer, AdsEncoder

#
# Using ads_client, you can publish a message towards ADS
#
ads_client = None
ads_encoder = None


async def temperature_handler(msg):
    """This is the handler function that gets registered for `simulation/temperature`.
    The received data is encoded using `Apache avro` with the schema from the file `edgefarm/avro_schemas/dataSchema.avro`.

    This example unpacks the original message and encodes it into an ADS_DATA avro message (see `edgefarm/ads-schemas/ads_data.avsc`).
    The payload in ADS_DATA is another AVRO message with a schema for a temperature sensor (see `edgefarm/ads-schemas/temperature_data.avsc`)
    The whole ADS_DATA message is then sent to ads-node module.
    """
    message = avro.schema_decode(io.BytesIO(msg.data))

    org_payload = json.loads(message["payload"])
    if org_payload["sensorname"] == "temperature":
        print(org_payload)

        # Generate an ADS payload with "temperature_data" schema
        ads_payload = {
            "meta": {"version": b"\x01\x00\x00"},
            "data": {
                "time": datetime.datetime.utcfromtimestamp(
                    int(org_payload["timestamp"])
                ),
                "temp": float(org_payload["value"]),
            },
        }
        ads_data_binary = ads_encoder.encode(
            tags=[{"key": "mon", "value": "true"}],
            payload_schema="temperature_data",
            schema_version=b"\x01\x00\x00",
            data=ads_payload,
        )
        # Send data to ads node module
        await ads_client.publish(ads_data_binary)
    else:
        print(f"Received unknown payload: {org_payload}")


# You can register multiple handlers for the same MQTT topic.
# Example:
# topics = {
#   'simulation/temperature': [temp_handler1, temp_handler2],
#   'simulation/acceleration': [accel_handler]
# }
topics = {"simulation/temperature": [temperature_handler]}

# This is to store corresponding nats subjects to handler functions for specific MQTT topics.Exception
# Example for accessing subjects from topics example above:
# Let's access the corresponding nats subject for `temp_handler2` for `simulation/temperature`
# print(subjects["simulation/temperature"][1])
subjects = {}


async def run(loop):
    global ads_client, ads_encoder

    # Connect to ALM MQTT module and register the MQTT subjects we want to receive
    client = AlmMqttModuleClient(loop)
    await client.connect()
    try:
        for key in topics:
            print("Registering to '{}'".format(key))
            for handler in topics[key]:
                subject = await client.subscribe(key, handler)
                if key not in subjects:
                    subjects[key] = list()
                subjects[key].append(subject)
                print("-> corresponding nats subject: '{}'".format(subject))
    except Exception as e:
        sys.stderr.write(f"Error: '{e}'")
        exit(1)

    # Connect to NATS to publish to "ads" subject which is consumed by ADS Node module
    ads_client = AdsProducer(loop)
    await ads_client.connect()

    # Instantiate an ADS DATA encoder to produce the ADS avro message
    # Register the embedded data schemas (here: temperature data)
    # If you need further schemas, add them to the list of <payload_schemas>

    device_id = os.getenv('IOTEDGE_DEVICEID', 'no-device-id')
    ads_encoder = AdsEncoder(
        app="HVAC", module=f"{device_id}.hvac", payload_schemas=["temperature_data"]
    )

    def signal_handler():
        print("Unsubscribing and shutting down...")
        loop.create_task(client.close())

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()
