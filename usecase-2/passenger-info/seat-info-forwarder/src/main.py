import os
import signal
import asyncio
import nats.aio.errors as NatsError
import json

from edgefarm_application.base.application_module import application_module_network_nats
import edgefarm_application as ef
from edgefarm_application.base.avro import schemaless_decode
from edgefarm_application.base.avro import schemaless_encode
from schema_loader import schema_load


# enable use of mqtt client and nats connection in seat_info_request_handler
mqtt_client = None
nc = None

mqtt_req_topic = "pis/req/seatRes"
mqtt_res_topic = "pis/res/seatRes"
# nats subject needs to start with `public.` to enable access to clound module
nats_subject = "public.pis.seatRes"


async def seat_info_request_handler(msg):
    """This is the handler function that gets registered for `pis/req/seatRes`.
    The received data is a python dictionary.
    msg['payload'] is the MQTT message as received from MQTT. Here, the payload is
    a string containing the train ID.

    This example encodes the data it into an seat_info_request avro message (see `../schemas/seat_info_request.avsc`).
    The message is transmitted via nats request reply to the cloud module, which responses with a seat_info_response avro message (see `../schemas/seat_info_response.avsc`).
    The received data contains the reserved seats and is replied to the MQTT topic `pis/res/seatRes`.
    """

    # Generate payload with "seat_info_request" schema
    train = msg["payload"].decode("utf-8")
    print("Train ID: " + train)

    seat_info_request = {
        "train": train,
    }

    # Pass request to clound module
    try:
        response = await nc.request(
            nats_subject,
            schemaless_encode(
                seat_info_request, schema_load(__file__, "seat_info_request")
            ),
            timeout=2,
        )

        m = schemaless_decode(
            response.data, schema_load(__file__, "seat_info_response")
        )
        seat_reservations = []
        for seat_info in m["seatReservations"]:
            seat_reservations.append(
                {
                    "id": seat_info["id"],
                    "startStation": seat_info["startStation"],
                    "endStation": seat_info["endStation"],
                }
            )

        print("Seat reservations received:")
        print(seat_reservations)

        # Send seat reservations response
        json_dump = json.dumps(seat_reservations).encode()
        await mqtt_client.publish(mqtt_res_topic, json_dump)
    except (NatsError.NatsError, NatsError.ErrTimeout) as e:
        print("error: " + str(e))


async def main():
    global nc, mqtt_client
    loop = asyncio.get_event_loop()

    # Initialize EdgeFarm SDK
    if os.getenv("IOTEDGE_MODULEID") is not None:
        await ef.application_module_init_from_environment(loop)
    else:
        print("Warning: Running example outside IOTEDGE environment")
        await ef.application_module_init(loop, "", "", "")

    # Connect to EdgeFarm service module mqtt-bridge and register the MQTT subjects
    mqtt_client = ef.AlmMqttModuleClient()
    print("Registering to " + mqtt_req_topic)
    await mqtt_client.subscribe(mqtt_req_topic, seat_info_request_handler)

    # # Get nats connection
    nc = application_module_network_nats()

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
    asyncio.run(main())
