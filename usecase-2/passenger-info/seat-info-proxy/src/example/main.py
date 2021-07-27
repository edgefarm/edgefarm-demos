import argparse
import logging
import sys
import os
import time
import asyncio

from nats import *  # noqa

from edgefarm_application.base.avro import schemaless_decode, schemaless_encode

import schema_loader

__author__ = "Florian Reinhold"
__copyright__ = "Ci4Rail GmbH"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def parse_args(args):

    parser = argparse.ArgumentParser(
        description="Preload DB with seat reservation data"
    )
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

    args = parse_args(args)
    setup_logging(args.loglevel)

    _timestamp_codec = schema_loader.schema_load(__file__, "timestamp")
    _seat_info_request_codec = schema_loader.schema_load(__file__, "seat_info_request")
    _seat_info_response_codec = schema_loader.schema_load(
        __file__, "seat_info_response"
    )

    nats_server = os.getenv("NATS_SERVER", "nats://localhost:4222")

    nc = NATS()  # noqa

    await nc.connect(servers=[nats_server])

    for i in range(100):

        # get update timestamp
        try:
            msg = await nc.request("seat_info_proxy.data_timestamp", b"", timeout=1)
            # Use the response
            data = schemaless_decode(msg.data, _timestamp_codec)
            print("sync time:", data["data"]["time"])
        except asyncio.TimeoutError:
            print("Timed out waiting for response")

        # get reservation data
        try:
            req = {"train": "ICE 1"}
            data = schemaless_encode(req, _seat_info_request_codec)
            msg = await nc.request("seat_info_proxy.data", data, timeout=1)

            data = schemaless_decode(msg.data, _seat_info_response_codec)
            print("reservation data: \n", data)
        except asyncio.TimeoutError:
            print("Timed out waiting for response")
        time.sleep(.1)

    _logger.info("Done!")


def run():
    asyncio.run(main(sys.argv[1:]))


if __name__ == "__main__":
    run()
