from pydantic import BaseModel

class CreateBet(BaseModel):
    lot_id: int
    bet_value: int
    user_id: int

    class Config:
        orm_mode = True

class GetBet(BaseModel):
    lot_id: int
    bet_value: int
    user_id: int

    class Config:
        orm_mode = True

class CreateLot(BaseModel):
    start_bet: int
    description: str

    class Config:
        orm_mode = True

class GetLot(BaseModel):
    id: int
    owner_id: int
    start_bet: int
    description: str
    bets: list[CreateBet] = []

    class Config:
        orm_mode = True
