from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

import models
import logging


_logger = logging.getLogger(__name__)
_update = None

# Session to the database to query the data from
# SourceSession = None
source_engine = None

# Session to the database to store the cache in
# DestSession = None
# dest_engine = None


# Init database connections 'sqlite:///:memory:'
async def init(source_db_uri, dest_db_uri):

    # global SourceSession, DestSession, source_engine, dest_engine
    global source_engine
    source_engine = create_async_engine(source_db_uri, echo=True)


async def get(trainid):

    async with source_engine.connect() as conn:

        # select a Result, which will be delivered with buffered
        # results
        result = await conn.execute(select(models.SeatReservation).where(models.SeatReservation.trainid == trainid))
        r = result.fetchall()
        logging.debug(r)
        return r


# Sync source and destination db seatreservation tables
async def sync():

    global _update
    _update = datetime.now()
    _logger.debug("cache syncronized.")
    return _update
