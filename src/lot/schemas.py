from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel
from datetime import datetime

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

    class Config:
        orm_mode = True

class GetLot(BaseModel):
    id: int
    owner_id: int
    start_bet: int
    description: str
    end_date: datetime
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

    # bets: list[BetBase] = []

