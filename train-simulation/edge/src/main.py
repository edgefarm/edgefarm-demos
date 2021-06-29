import os
import signal
import asyncio
import datetime
import json
import logging
import edgefarm_application as ef
from edgefarm_application.base.schema import schema_read_builtin

#
# Using the ads_producer/encoder, you can publish a message towards ADS
#
ads_producer = None
ads_encoder = None


async def temperature_handler(msg):
    """ This is the handler function that gets registered for `simulation/temperature`.
    The received data is a python dictionary.
    msg['payload'] is the MQTT message as received from MQTT. Here, the payload is
    a json message, so we convert the json to a python dictionary.

    This example encodes the data it into an ADS_DATA avro message.
    The payload in ADS_DATA is another AVRO message with a schema for a temperature sensor (see `schemas/temperature_data.avsc`)
    The whole ADS_DATA message is then sent to ads-node module.
    """
    org_payload = json.loads(msg["payload"])
    print(f"{msg}: payload={org_payload}")

    if org_payload["sensorname"] == "temperature":
        print(org_payload)

        # Generate an ADS payload with "temperature_data" schema
        ads_payload = {
            "meta": {"version": b"\x01\x00\x00"},
            "data": {
                "time": datetime.datetime.fromtimestamp(
                    int(org_payload["timestamp"])
                ),
                "temp": float(org_payload["value"]),
            },
        }
        # Send data to ads node module
        await ads_producer.encode_and_send(ads_encoder, ads_payload)
    else:
        print(f"Received unknown payload: {org_payload}")


# List of mqtt topics and corresponding handlers
# Example:
# topics = {
#   'simulation/temperature': temp_handler,
#   'simulation/acceleration': accel_handler
# }
topics = {"simulation/temperature": temperature_handler}


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

    # Create an encoder for an application specific payload
    payload_schema = schema_read_builtin(__file__, "schemas/temperature_data.avsc")
    ads_encoder = ef.AdsEncoder(
        payload_schema,
        schema_name="temperature_data",
        schema_version=(1, 0, 0),
        tags={"monitor": "channel1"},
    )

    # Connect to ALM MQTT module and register the MQTT subjects we want to receive
    mqtt_client = ef.AlmMqttModuleClient()
    for mqtt_topic, handler in topics.items():
        print(f"Registering to '{mqtt_topic}'")
        await mqtt_client.subscribe(mqtt_topic, handler)

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
    await mqtt_client.close()
    await ef.application_module_term()


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get('LOGLEVEL', 'INFO').upper(),
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())
