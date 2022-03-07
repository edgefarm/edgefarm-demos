
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class SeatReservation(Base):

    __tablename__ = 'seat_reservation'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    trainid = Column(String)
    seatid = Column(Integer)
    startstation = Column(String)
    endstation = Column(String)

    def __repr__(self):
        return "<SeatReservation(trainid='{}', seatid='{}', startstation={}, endstation={})>"\
                .format(self.trainid, self.seatid, self.startstation, self.endstation)
