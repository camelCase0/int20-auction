import os
from auth.models import User
from fastapi import APIRouter, File, UploadFile, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    
    if lot is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    bets = await session.execute(select(Bet).filter(Bet.lot_id==lot_id).limit(20))

    response_lot = GetLot(
        id=lot.id,
        owner_id=lot.owner_id,
        start_bet=lot.start_bet,
        description=lot.description,
        bets=bets # MAY BE ERROR
    )
    return response_lot


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

