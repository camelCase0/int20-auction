from datetime import datetime
import os

from fastapi.responses import FileResponse
from auth.models import User
from fastapi import APIRouter, File, UploadFile, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from main import fastapi_users
from lot.schemas import GetLot, CreateLot
from lot.models import Lot, Bet 
from database import get_async_session
from fastapi import HTTPException, status
from typing import IO
import filetype

router = APIRouter(
    prefix="/lot",
    tags=["Auction"]
)
IMAGEDIR= "images/"

current_user = fastapi_users.current_user()

@router.get("/{lot_id}/")#,response_model=GetLot
async def get_lot_by_id(lot_id:int, session: AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)
    file_path = f"{IMAGEDIR}{lot_id}"

    if lot is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # bets = await session.execute(select(Bet).filter(Bet.lot_id==lot_id).limit(20))
    bet_dicts = [{"lot_id": bet.lot_id,"bet_id": bet.bet_id, "bet_value": bet.value, "user_id": bet.user_id} for bet in lot.bets]
    response_lot = GetLot(
        id=lot.id,
        owner_id=lot.owner_id,
        start_bet=lot.start_bet,
        description=lot.description,
        end_date=lot.end_date,
        bets=bet_dicts # MAY BE ERROR
    )
    # FileResponse(path=file_path, filename=lot_id, media_type='multipart/form-data'),
    return response_lot

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
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
    ):
    validate_file_size_type(file)

    new_op = Lot(start_bet=start_bet, description=description, owner_id=user.id)
    session.add(new_op)
    await session.commit()
    session.refresh(new_op)

    filename = f"{IMAGEDIR}{new_op.id}"
    contents = await file.read()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename,"wb") as f:
        f.write(contents)

    return new_op

@router.post("/{lot_id}/", status_code=201)
async def create_bet(lot_id:int, new_value:int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)

    if (datetime.utcnow()>lot.end_date):
        raise HTTPException(status_code=403, detail="Lot is finished")
    

    # mbet = await session.select(Bet).filter(Bet.lot_id==lot_id).order_by(Bet.value.desc()).limit(1)
    mbet = await session.execute(select(func.max(Bet.value)))
    max_bet = mbet.scalar()
    if max_bet is None:
        max_bet = lot.start_bet

    if (max_bet > new_value):
        raise HTTPException(status_code=406, detail="Bet must be higher")

    new_bet = Bet(
        user_id=user.id,
        value=new_value,
        lot_id=lot_id
    )
    session.add(new_bet)
    await session.commit()
    session.refresh(new_bet)
    return new_bet

@router.delete("/{lot_id}")
async def delete_lot(lot_id:int, user:User= Depends(current_user), session:AsyncSession = Depends(get_async_session)):
    lot = await session.get(Lot,lot_id)
    if lot.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You are not permited to delete this lot")
    statement = delete(Lot).where(Lot.id == lot_id)
    await session.execute(statement)
    await session.commit()

    return 200

# @router.get("/{lot_id}/", status_code=201)