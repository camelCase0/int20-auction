from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from chat.models import Message
from chat.schemas import MessagesModel
from database import async_session_maker, get_async_session
from lot.models import Lot

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str,chat_id: int, add_to_db: bool):
        if add_to_db:
            await self.add_messages_to_database(message, chat_id)
        for connection in self.active_connections:
            await connection.send_text(message)

    @staticmethod
    async def add_messages_to_database(message: str, lot_id: id):
        async with async_session_maker() as session:
            stmt = insert(Message).values(
                text=message,
                lot_id=lot_id
            )
            await session.execute(stmt)
            await session.commit()



@router.get("/{lot_id}/last_messages/")
async def get_last_messages(lot_id:int,
        session: AsyncSession = Depends(get_async_session)
) -> List[MessagesModel]:
    query = select(Message).filter(Message.lot_id == lot_id).order_by(Message.id.desc()).limit(5)
    messages = await session.execute(query)
    return messages.scalars().all()

chat_dict = {}
@router.websocket("/{chat_id}/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id:int, client_id: int):
    if chat_id not in chat_dict:
        manager = ConnectionManager()
        chat_dict[chat_id] = manager

    manager = chat_dict[chat_id]
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}",chat_id=chat_id, add_to_db=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat",chat_id=chat_id, add_to_db=False)
    
@router.websocket("/ws/bid/{lot_id}")
async def websocket_bid_endpoint(websocket: WebSocket, lot_id: int, session: AsyncSession = Depends(get_async_session)):
    
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        bid_value = float(data)
        auction_item = await session.get(Lot, lot_id)
        if auction_item is None:
            raise HTTPException(status_code=404, detail="Auction item not found")
        await websocket.send_text(f"{lot_id}:{bid_value}")
    # try:
    #     await websocket.accept()
    #     if chat_id not in chat_dict:
    #         chat_dict[chat_id] = Room(chat_id)

    #     room  = chat_dict[chat_id]
    #     room.connections.append(websocket)

    #     print(f"connection established for {client_id} in room {chat_id}")

    #     while True:
    #         data = await websocket.receive_text()
    #         await room.broadcast(data, websocket)
    # except WebSocketDisconnect:
    #     if chat_id not in chat_dict:
    #         room = chat_dict[chat_id]
    #         room.connections.remove(websocket)
    #         if len(room.connections) == 0:
    #             del chat_dict[chat_id]


#client_id = user.id
    # await manager.connect(websocket)
    # try:
    #     while True:
    #         data = await websocket.receive_text()
    #         await manager.broadcast(f"Client #{client_id} says: {data}",chat_id=chat_id, add_to_db=True)
    # except WebSocketDisconnect:
    #     manager.disconnect(websocket)
    #     await manager.broadcast(f"Client #{client_id} left the chat",chat_id=chat_id, add_to_db=False)

# @router.websocket("/ws/{user_id}")
# async def websocket_endpoint(user_id: str, websocket: WebSocket):
#     await websocket.accept()

#     # Store the WebSocket connection in the dictionary
#     connected_users[user_id] = websocket

#     try:
#         while True:
#             data = await websocket.receive_text()
#             # Send the received data to the other user
#             for user, user_ws in connected_users.items():
#                 if user != user_id:
#                     await user_ws.send_text(data)
#     except:
#         # If a user disconnects, remove them from the dictionary
#         del connected_users[user_id]
#         await websocket.close()