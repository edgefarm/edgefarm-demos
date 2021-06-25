from datetime import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DropTable, CreateTable
import models
import logging

from sqlalchemy.sql.expression import update

_logger = logging.getLogger(__name__)
_update = None

# Session to the database to query the data from
SourceSession = None
source_engine = None

# Session to the database to store the cache in
DestSession = None
dest_engine = None


# Init database connections 'sqlite:///:memory:'
def init(source_db_uri, dest_db_uri):

    global SourceSession, DestSession, source_engine, dest_engine
    source_engine = create_engine(source_db_uri, echo=True)
    SourceSession = sessionmaker(source_engine)

    dest_engine = create_engine(dest_db_uri, echo=True)
    DestSession = sessionmaker(dest_engine)

    _logger.info("Cleanup cache...")
    try:
        models.SeatReservation.__table__.drop(dest_engine)
    except OperationalError:
        _logger.info("No cache to clean up")

    # Create Table
    _logger.info("(Re-)creating cache...")
    models.SeatReservation.__table__.create(dest_engine)


def get(trainid):

    query = SourceSession().query(models.SeatReservation).filter(models.SeatReservation.trainid == trainid)
    return query


# Sync source and destination db seatreservation tables
def sync():

    global _update
    _update = datetime.now()
    _logger.debug("cache syncronized.")
    return _update