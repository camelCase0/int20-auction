
from sqlalchemy import Column, Integer, LargeBinary, String, ForeignKey, DateTime, Double, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base
from auth.models import User
from enum import Enum

class Lot_type(str, Enum):
    CREATIVE = "CREATIVE"
    FOR_KIDS = "FOR_KIDS"
    REALTY = "REALTY"
    ELECTRONICS = "ELECTRONICS"
    ANTIQUES = "ANTIQUES"
    FOR_HOME = "FOR_HOME"

class Money_aim(str,Enum):
    CHILDREN = "CHILDREN"
    ARMY = "ARMY"
    DISPLACED = "DISPLACED"
    CANCER = "CANCER"
    DISABLED = "DISABLED"

class Lot(Base):
    __tablename__ = "lot"

    id = Column(Integer, primary_key=True)
    start_bet = Column(Integer, nullable=False)
    description = Column(String(length=255))
    owner_id = Column(Integer)
    end_date = Column(DateTime, default=datetime.utcnow()+timedelta(days=1))

    lot_type = Column(String)
    money_aim = Column(String)

    image_data = Column(LargeBinary)

    bets = relationship("Bet", back_populates="lot",lazy="selectin")

# class Image(Base):
#     __tablename__ = "images"

#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String)
#     data = Column(String)

#     lots = relationship("Lot", back_populates="image")

class Bet(Base):
    __tablename__ = "bet"
    bet_id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow())
    user_id = Column(Integer)
    value = Column(Double)

    lot_id = Column(Integer, ForeignKey('lot.id'))
    lot = relationship("Lot", back_populates="bets")

    # user_id = Column(Integer, ForeignKey('user.c.id'))
    # user = relationship("User", back_populates="bets")

