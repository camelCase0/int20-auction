from pydantic import BaseModel


class MessagesModel(BaseModel):
    id: int
    text: str
    lot_id: int

    class Config:
        orm_mode = True