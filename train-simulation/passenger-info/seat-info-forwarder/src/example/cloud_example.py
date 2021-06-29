import os
import signal
import asyncio
from nats.aio.client import Client as Nats

import edgefarm_application as ef
from edgefarm_application.base.avro import schemaless_decode
from edgefarm_application.base.schema import schema_load_builtin
from edgefarm_application.base.avro import schemaless_encode


nc = None
nats_topic = "pis.seatRes"


async def nats_handler(msg):
    """Receive nats messages here."""

    # Decode received message
    seat_info_request = schemaless_decode(
        msg.data, schema_load_builtin(__file__, "../schemas/seat_info_request")
    )

    train = seat_info_request["train"]
    print("Train ID: " + train)

    # Prepare seat info data
    seat_info_response = {
        "seatReservations": [
            {"id": 0, "startStation": "Nürnberg", "endStation": "München"},
            {"id": 2, "startStation": "Erlangen", "endStation": "Frankf."},
            {"id": 5, "startStation": "Köln", "endStation": "Berlin"},
        ]
    }

    print("Seat Info: " + str(seat_info_response))

    resp_byte = schemaless_encode(
        seat_info_response,
        schema_load_builtin(__file__, "../schemas/seat_info_response"),
    )

    # Reply seat info data
    await nc.publish(msg.reply, resp_byte)


async def main():
    global nc
    loop = asyncio.get_event_loop()

    # Initialize EdgeFarm SDK
    await ef.application_module_init(loop, "", "", "")

    #
    # Connect to NATS and subscribe to "service.location" subject
    #
    nc = Nats()
    nats_server = os.getenv("NATS_SERVER", "nats:4222")
    await nc.connect(servers="nats://" + nats_server, loop=loop)
    print("NATS connect ok")

    subscription_id = await nc.subscribe(nats_topic, cb=nats_handler)

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
