import base64
from datetime import datetime
from io import BytesIO
import os

from fastapi.responses import FileResponse
import jwt
from auth.models import User
from fastapi import APIRouter, File, UploadFile, Depends, Body, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, func, delete
from config import SECRET_COOK
from main import fastapi_users
from lot.schemas import GetLot, CreateLot, GetLotAll, UpdateLot
from lot.models import Lot, Bet, Lot_type, Money_aim 
from database import get_async_session, async_session_maker
from fastapi import HTTPException, status
from typing import IO, Dict, List, Optional
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
    for record in records:
        record.image_data = base64.b64encode(record.image_data).decode('utf-8')
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
    lot_type: str = Body(...),
    money_aim: str = Body(...),
    end_date: datetime = Body(None),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    contents = await file.read()
    validate_file_size_type(file)

    encoded_image_data = base64.b64encode(contents)
    # contents = file.read()

    new_op = Lot(
        start_bet=start_bet, 
        description=description, 
        end_date=end_date, 
        owner_id=user.id,
        lot_type=lot_type, 
        money_aim=money_aim,
        image_data=encoded_image_data)
    session.add(new_op)
    await session.commit()
    await session.refresh(new_op)

    # filename = f"{IMAGEDIR}{new_op.id}"
    # contents = await file.read()
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    # with open(filename,"wb") as f:
    #     f.write(contents)

    return new_op

@router.get("/{lot_id}/")#,response_model=GetLot
async def get_lot_by_id(lot_id:int, session: AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)
    # file_path = f"{IMAGEDIR}{lot_id}"

    if lot is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # bets = await session.execute(select(Bet).filter(Bet.lot_id==lot_id).limit(20))
    bet_dicts = [{"lot_id": bet.lot_id,"bet_id": bet.bet_id, "bet_value": bet.value, "user_id": bet.user_id} for bet in lot.bets]
    
    
    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=404, detail="Image not found")
    
    # with open(file_path, 'rb') as f:
    #     image_data = f.read()
    
    # FileResponse(path=file_path, filename=lot_id, media_type='multipart/form-data'),
    # image_data = base64.b64encode(image_data).decode('utf-8')

    response_lot = GetLot(
        id=lot.id,
        owner_id=lot.owner_id,
        start_bet=lot.start_bet,
        description=lot.description,
        end_date=lot.end_date,
        image_data=lot.image_data,
        lot_type=lot.lot_type,
        money_aim=lot.money_aim,
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
    lot.lot_type=form.lot_type
    lot.image_data=form.image_data
    lot.money_aim=form.money_aim

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
class AuctionConnectionManager:
    def __init__(self):
        self.auction_connections: Dict[any, list] = {}

    async def connect(self, websocket: WebSocket, lot_id):
        await websocket.accept()
       
        if not self.auction_connections.get(lot_id):
            self.auction_connections[lot_id] = []
        self.auction_connections[lot_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, lot_id):
        self.auction_connections[lot_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket,
                                    cur_price=None, json_data=None):
        await websocket.send_text(message)
        if cur_price:
            await websocket.send_json({'new_value': cur_price})
        if json_data:
            #print(json_data)
            await websocket.send_json({'json_data': json_data})

    async def broadcast(self, message: str, user_id:int, new_value:int, lot_id: id):
        for connection in self.auction_connections.get(lot_id):
            await self.add_messages_to_database(user_id, new_value, lot_id)
            await connection.send_text(message)
            payload = {}
            if new_value:
                payload = {'new_value': new_value,
                           'user_id': user_id}
            if payload.keys():
                await connection.send_json(payload)
    @staticmethod
    async def add_messages_to_database(user_id:int, new_value:int, lot_id: id):
        async with async_session_maker() as session:
            
            item = await session.get(Lot, lot_id)
            
            item.start_bet = new_value
            await session.commit()

            new_bet = Bet(
                    user_id=user_id,
                    value=new_value,
                    lot_id=lot_id
                )
            session.add(new_bet)
            await session.commit()
    
    @staticmethod
    async def get_lot(lot_id:int):
        async with async_session_maker() as session:
             lot_found = await session.get(Lot, lot_id)
             return lot_found


manager = AuctionConnectionManager()
session = get_async_session()
@router.websocket('/{lot_id}/ws/bets/')
async def auction(websocket: WebSocket, lot_id: int):
    await manager.connect(websocket, lot_id)
    try:
        cookie = websocket._cookies['Auction']
        ss = jwt.decode(cookie, SECRET_COOK, audience='fastapi-users:auth', algorithms=["HS256"])
        user_id = ss['sub']
        if user_id:
            while True:
                user_id = int(user_id)
                data = await websocket.receive_json()
                new_value = data.get('new_value')
                if not new_value:
                    continue
                new_value = int(new_value)     
                item = await manager.get_lot(lot_id)
                if not item:
                    continue         
                if item.start_bet>=new_value:
                    continue  
                if (item.end_date < datetime.utcnow()):
                    await manager.send_personal_message("The auction is already finished!", websocket)
                    await manager.send_personal_message(f"{item.id} was sold for {item.start_bet}!", websocket)
                    await manager.send_personal_message(message="", websocket=websocket, json_data={'completed': True})
                    
                await manager.broadcast(f"Participant {user_id} has bid {item.start_bet}!", 
                                        lot_id=lot_id, 
                                        user_id=user_id,
                                        new_value=new_value)
                
                # item = await session.get(Lot, lot_id)
                # if item.start_bet>=new_value:
                #     continue
                # item.start_bet = new_value
                # await session.commit()

                # new_bet = Bet(
                #     user_id=user_id,
                #     value=new_value,
                #     lot_id=lot_id
                # )
                # session.add(new_bet)
                # await session.commit()
                # await session.refresh(new_bet)

                # await manager.broadcast(f"Participant {user_id} has bid {item.start_bet}!", auction_id=lot_id, new_value=new_bet.value)
                # session.commit()

    except WebSocketDisconnect:
        await manager.disconnect(websocket, lot_id)
        await manager.broadcast(f"Participant {user_id} has left the auction", auction_id=lot_id)