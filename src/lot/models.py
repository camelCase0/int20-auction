from sqlalchemy import Column, Integer, String

from database import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    start_bet = Column(String(length=50), nullable=False)
    description = Column(String(length=255))
    foto = Column