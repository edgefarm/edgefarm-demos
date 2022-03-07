import argparse
import logging
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError

import models

from seat_info_proxy import __version__

import yaml

__author__ = "Florian Reinhold"
__copyright__ = "Ci4Rail GmbH"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def parse_args(args):

    parser = argparse.ArgumentParser(description="Preload DB with seat reservation data")
    parser.add_argument(
        "--version",
        action="version",
        version="seat-info-proxy {ver}".format(ver=__version__),
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

    parser.add_argument(
        "-f",
        "--file",
        dest="filename",
        required=True,
        help="input yaml"
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


def main(args):

    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting preloading db...")

    database_uri = os.getenv("DATABASE_URI", "sqlite:///seatinfos.db")

    # Connect to db
    engine = create_engine(database_uri)

    # Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    # Delete Table
    _logger.info("Cleanup table...")
    try:
        models.SeatReservation.__table__.drop(engine)
    except ProgrammingError:
        _logger.info("No table to clean up")
    except OperationalError:
        _logger.info("No table to clean up")

    # Create Table
    _logger.info("(Re-)creating table...")
    models.SeatReservation.__table__.create(engine)

    _logger.info("Loading json...")
    with open(args.filename, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            _logger.error(exc)

    try:
        _logger.info("Creating Records...")
        for i in data:
            record = models.SeatReservation(**{
                'trainid': i["trainid"],
                'seatid': i["seatid"],
                'startstation': i["startstation"],
                'endstation': i["endstation"]
            })
            print(record)
            s.add(record)  # Add all the records
        _logger.info("Attempt to commit all the records...")
        s.commit()
    except Exception as e:
        _logger.error("Errors while adding seatreservation data. Rollback.")
        _logger.error('Exception: ' + str(e))
        s.rollback()
    finally:
        s.close()  # Close the connection

    _logger.info("Done!")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
