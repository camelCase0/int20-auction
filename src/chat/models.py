from sqlalchemy import Column, Integer, String

from database import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    text = Column(String)