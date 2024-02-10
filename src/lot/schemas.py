from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel
from datetime import datetime

from lot.models import Lot_type, Money_aim

class CreateBet(BaseModel):
    lot_id: int
    bet_value: int
    user_id: int

    class Config:
        orm_mode = True

class GetBet(BaseModel):
    bet_id: int
    lot_id: int
    bet_value: int
    user_id: int

    class Config:
        orm_mode = True

class CreateLot(BaseModel):
    start_bet: int
    description: str
    end_date: datetime
    lot_type: Lot_type
    money_aim: Money_aim

    image_data: bytes

    class Config:
        orm_mode = True


class GetLotAll(BaseModel):
    id: int
    owner_id: int
    start_bet: int
    description: str
    end_date: datetime
    lot_type: Lot_type
    money_aim: Money_aim

    image_data: bytes

    class Config:
        orm_mode = True

class GetLot(BaseModel):
    id: int
    owner_id: int
    start_bet: int
    description: str
    end_date: datetime
    lot_type: Lot_type
    money_aim: Money_aim

    image_data: bytes

    bets: list[GetBet] = []

    class Config:
        orm_mode = True

class BetBase(BaseModel):
    bet_id: int
    user_id: int
    lot_id: int
    value: float
    date: datetime


class UpdateLot(BaseModel):
    # id: int
    start_bet: int
    description: str
    end_date: datetime
    lot_type: Lot_type
    money_aim: Money_aim

    image_data: bytes

    # bets: list[BetBase] = []

