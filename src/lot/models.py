from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from auth.models import User

class Lot(Base):
    __tablename__ = "lot"

    id = Column(Integer, primary_key=True)
    start_bet = Column(Integer, nullable=False)
    description = Column(String(length=255))
    owner_id = Column(Integer)

    bets = relationship("Bet", back_populates="lot")

class Bet(Base):
    __tablename__ = "bet"
    bet_id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow())

    lot_id = Column(Integer, ForeignKey('lot.id'))
    lot = relationship("Lot", back_populates="bets")

    # user_id = Column(Integer, ForeignKey('user.c.id'))
    # user = relationship("User", back_populates="bets")

