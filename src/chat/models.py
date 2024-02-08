from sqlalchemy import Column, Integer, String

from database import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    lot_id = Column(Integer)

# class Room:
#   def __init__(self, room_id):
#     self.room = room_id
#     self.connections = []

#   async def broadcast(self, message, sender):
#     for connection in self.connections:
#       print(message)
#       await connection.send_text(message)