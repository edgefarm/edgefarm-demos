import argparse
import logging
import sys
import asyncio
import os
import signal

# edgefarm appication library
import edgefarm_application as ef

# local imports
from seat_info_proxy_service import SeatInfoProxyService

import cache

__author__ = "Florian Reinhold"
__copyright__ = "Ci4Rail GmbH"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def parse_args(args):

    parser = argparse.ArgumentParser(description="Seat information proxy")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):

    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


async def main(args):

    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting preloading db...")

    loop = asyncio.get_event_loop()

    database_uri = os.getenv("DATABASE_URI", "sqlite:///seatinfos.db")

    cache.init(database_uri, "sqlite:///:memory:")

    # Initialize EdgeFarm SDK
    if os.getenv("IOTEDGE_MODULEID") is not None:
        await ef.application_module_init_from_environment(loop)
    else:
        print("Warning: Running example outside IOTEDGE environment")
        await ef.application_module_init(
            loop, "SeatRes", "fleet-seat-info-monitor", "no-runtime-id"
        )

    # Create a queue that we will use to store events.
    event_q = asyncio.Queue()

    seat_info_proxy_service = SeatInfoProxyService(event_q)

    def signal_handler():
        event_q.put_nowait("stop")

    for sig in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    while True:
        event = await event_q.get()
        print(f"main loop: event {event}")
        if type(event) is str and event == "stop":
            break

    print("Shutting down...")
    seat_info_proxy_service.stop()
    await ef.application_module_term()


def run():
    asyncio.run(main(sys.argv[1:]))


if __name__ == "__main__":
    run()
