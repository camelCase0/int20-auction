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

    bets: list[GetBet] = []

    class Config:
        orm_mode = True
