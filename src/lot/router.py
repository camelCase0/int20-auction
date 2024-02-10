import base64
from datetime import datetime
from io import BytesIO
import os

from fastapi.responses import FileResponse
from auth.models import User
from fastapi import APIRouter, File, UploadFile, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, func, delete
from main import fastapi_users
from lot.schemas import GetLot, CreateLot, UpdateLot
from lot.models import Lot, Bet 
from database import get_async_session
from fastapi import HTTPException, status
from typing import IO, Optional
import filetype

router = APIRouter(
    prefix="/lot",
    tags=["Auction"]
)
IMAGEDIR= "images/"

current_user = fastapi_users.current_user()

@router.get("/", status_code=200)
async def get_lots(session: AsyncSession = Depends(get_async_session)):
    lots = await session.execute(select(Lot))
    records = lots.scalars().all()
    return records

def validate_file_size_type(file: IO):
    FILE_SIZE = 2097152 # 2MB

    accepted_file_types = ["image/png", "image/jpeg", "image/jpg", "image/heic", "image/heif", "image/heics", "png",
                          "jpeg", "jpg", "heic", "heif", "heics" 
                          ] 
    file_info = filetype.guess(file.file)
    if file_info is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unable to determine file type",
        )

    detected_content_type = file_info.extension.lower()

    if (file.content_type not in accepted_file_types
        or detected_content_type not in accepted_file_types):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )

    real_file_size = 0
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large")

@router.post("/new/", status_code=201)
async def create_lot(
    user: User = Depends(current_user),
    start_bet: int = Body(...),
    description: str = Body(...),
    end_date: datetime = Body(None),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    validate_file_size_type(file)

    new_op = Lot(start_bet=start_bet, description=description, end_date=end_date, owner_id=user.id)
    session.add(new_op)
    await session.commit()
    session.refresh(new_op)

    filename = f"{IMAGEDIR}{new_op.id}"
    contents = await file.read()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename,"wb") as f:
        f.write(contents)

    return new_op

@router.get("/{lot_id}/")#,response_model=GetLot
async def get_lot_by_id(lot_id:int, session: AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)
    file_path = f"{IMAGEDIR}{lot_id}"

    if lot is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # bets = await session.execute(select(Bet).filter(Bet.lot_id==lot_id).limit(20))
    bet_dicts = [{"lot_id": bet.lot_id,"bet_id": bet.bet_id, "bet_value": bet.value, "user_id": bet.user_id} for bet in lot.bets]
    
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    with open(file_path, 'rb') as f:
        image_data = f.read()
    
    # FileResponse(path=file_path, filename=lot_id, media_type='multipart/form-data'),
    image_data = base64.b64encode(image_data).decode('utf-8')

    response_lot = GetLot(
        id=lot.id,
        owner_id=lot.owner_id,
        start_bet=lot.start_bet,
        description=lot.description,
        end_date=lot.end_date,
        image_data=image_data,
        bets=bet_dicts #
    )

    return response_lot

@router.put("/{lot_id}/", status_code=200)
async def update_lot_by_id(lot_id:int, form:UpdateLot, user:User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    
    lot = await session.get(Lot,lot_id)
    if (lot.owner_id != user.id):
        raise HTTPException(status_code=403, detail="You are not owner of this LOT")

    if lot is None:
        raise HTTPException(status_code=404, detail="Lot not found")
    
    lot.start_bet = form.start_bet
    lot.description = form.description
    lot.end_date = form.end_date

    await session.commit()
    session.refresh(lot)

    return lot

@router.post("/{lot_id}/", status_code=201)
async def create_bet(lot_id:int, new_value:int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)

    if (datetime.utcnow()>lot.end_date):
        raise HTTPException(status_code=403, detail="Lot is finished")
    
    # mbet = await session.select(Bet).filter(Bet.lot_id==lot_id).order_by(Bet.value.desc()).limit(1)
    mbet = await session.execute(select(Bet).filter(Bet.lot_id == lot_id).order_by(desc(Bet.value)).limit(1))

    max_bet = mbet.scalars().first()
    if max_bet is None:
        max_bet = lot.start_bet
    else:
        max_bet = max_bet.value

    if (max_bet >= new_value):
        raise HTTPException(status_code=406, detail="Bet must be higher")
    lot.start_bet = new_value
    await session.commit()

    new_bet = Bet(
        user_id=user.id,
        value=new_value,
        lot_id=lot_id
    )
    session.add(new_bet)
    await session.commit()
    await session.refresh(new_bet)
    return new_bet

@router.delete("/{lot_id}") # delete lot
async def delete_lot(lot_id:int, user:User= Depends(current_user), session:AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)
    if lot.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You are not permited to delete this lot")
    
    await session.execute(delete(Bet).where(Bet.lot_id == lot_id))

    statement = delete(Lot).where(Lot.id == lot_id)
    await session.execute(statement)
    await session.commit()

    return 200

# @router.get("/{lot_id}/", status_code=201)
############################################
# class AuctionConnectionManager:
#     def __init__(self):
#         self.auction_connections: Dict[any, list] = {}

#     async def connect(self, websocket: WebSocket, auction_id):
#         await websocket.accept()
#         item_found = session.get(AuctionItem, auction_id)
#         #print(item_found)
#         if (item_found.ends and item_found.ends < datetime.datetime.now()) \
#                 or item_found.completed:
#             item_found.completed = True
#             await self.send_personal_message("The auction is already finished!",
#                                          websocket)
#             await self.send_personal_message(f"{item_found.item_name} was sold for {item_found.bid}"
#                                              f" to a bidder #{item_found.bidder_id}!",
#                                              websocket)
#             await self.send_personal_message(message="", websocket=websocket,
#                                              json_data={'completed': True})
#             session.commit()
#             return
#         cur_bid = item_found.bid

#         if cur_bid:
#             await self.send_personal_message("The auction has already started!",
#                                              websocket, cur_bid)
#         if not self.auction_connections.get(auction_id):
#             self.auction_connections[auction_id] = []
#         self.auction_connections[auction_id].append(websocket)

#     async def disconnect(self, websocket: WebSocket, auction_id):
#         self.auction_connections[auction_id].remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket,
#                                     cur_price=None, json_data=None):
#         await websocket.send_text(message)
#         if cur_price:
#             await websocket.send_json({'new_price': cur_price})
#         if json_data:
#             #print(json_data)
#             await websocket.send_json({'json_data': json_data})

#     async def broadcast(self, message: str, auction_id: int, new_price=None, ends=None):
#         for connection in self.auction_connections.get(auction_id):
#             await connection.send_text(message)
#             payload = {}
#             if new_price:
#                 payload = {'new_price': new_price}
#             if ends:
#                 payload.update(ends=str(ends))
#             if payload.keys():
#                 await connection.send_json(payload)


# manager = AuctionConnectionManager()

# @router.websocket('/auction/{id}/ws/{participant_id}')
# async def auction(websocket: WebSocket, id: int, participant_id: int):
#     await manager.connect(websocket, id)
#     try:
#         while True:
#             data = await websocket.receive_json()
#             item = session.get(AuctionItem, id)
#             step = item.price_step | 0
#             current_bid = item.bid or 0
#             min_new_bid = current_bid + step if current_bid != item.min_price else current_bid
#             new_bid = data.get('bid')
#             if not new_bid:
#                 print(1)
#                 continue
#             if participant_id == item.bidder_id or not new_bid > current_bid:
#                 print(2)
#                 continue
#             if item.min_price <= new_bid >= min_new_bid:
#                 item.bid = new_bid
#                 item.bidder_id = participant_id
#                 item.ends = datetime.datetime.now() + datetime.timedelta(seconds=60)
#                 await manager.broadcast(f"Participant {participant_id} has bid {item.bid}!", auction_id=id, new_price=item.bid,
#                                         ends=item.ends)
#                 session.commit()

#     except WebSocketDisconnect:
#         await manager.disconnect(websocket, id)
#         await manager.broadcast(f"Participant has left the auction", auction_id=id)