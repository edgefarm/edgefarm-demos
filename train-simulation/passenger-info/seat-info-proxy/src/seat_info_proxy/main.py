import argparse
import logging
import sys
import asyncio
import os
import signal

# edgefarm appication library
import edgefarm_application as ef
from edgefarm_application.base.application_module import application_module_network_nats

# local imports
from .seat_info_proxy_service import SeatInfoProxyService

from seat_info_proxy import __version__

from . import cache
from db import config

__author__ = "Florian Reinhold"
__copyright__ = "Ci4Rail GmbH"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version="seat-info-proxy {ver}".format(ver=__version__),
    )
    parser.add_argument(dest="n", help="n-th Fibonacci number", type=int, metavar="INT")
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
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

async def main(args):
    loop = asyncio.get_event_loop()

    cache.init(config.DATABASE_URI,'sqlite:///:memory:')

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

    seat_info_proxy_service = SeatInfoProxyService()

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
    await seat_info_proxy_service.stop()
    await ef.application_module_term()


def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
