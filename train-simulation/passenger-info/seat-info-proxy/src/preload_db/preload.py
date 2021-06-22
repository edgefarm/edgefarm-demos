import argparse
import logging
import sys

from numpy import genfromtxt
from time import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
import os.path

from seat_info_proxy import __version__

from db import config
from db import models

__author__ = "Florian Reinhold"
__copyright__ = "Ci4Rail GmbH"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
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
        help="input csv",
        metavar="FILE",
        type=lambda x: is_valid_file(parser, x)
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
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting preloading db...")

    # Connect to db
    engine = create_engine(config.DATABASE_URI)

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

    # Create Table
    _logger.info("(Re-)creating table...")
    models.SeatReservation.__table__.create(engine)

    try:

        _logger.info("Loading csv...")
        file_name = args.filename
        data = genfromtxt(file_name, delimiter=';', skip_header=1, converters={0: lambda s: str(s)}).tolist()

        _logger.info("Creating Records...")
        for i in data:
            record = models.SeatReservation(**{
                'trainid' : i[0],
                'seatid' : i[1],
                'startstation' : i[2],
                'endstation' : i[3],
            })
            s.add(record) #Add all the records
        _logger.info("Attempt to commit all the records...")
        s.commit()
    except Exception as e:
        _logger.error("Errors while adding seatreservation data. Rollback.")
        _logger.error('Exception: '+ str(e))
        s.rollback()
    finally:
        s.close() #Close the connection

    _logger.info("Done!")

    # engine = create_engine(DATABASE_URI)
    # connection = engine.connect()
    # metadata = MetaData()
    # seat_reservation = Table('seat_reservation', metadata, autoload=True, autoload_with=engine)
    # print(seat_reservation.columns.keys())
    # print(repr(metadata.tables['seat_reservation']))

    # #Equivalent to 'SELECT * FROM census'
    # query = select([seat_reservation])
    # ResultProxy = connection.execute(query)
    # ResultSet = ResultProxy.fetchall()
    # print(ResultSet[:3])


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
