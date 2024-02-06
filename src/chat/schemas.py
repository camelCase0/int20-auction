from pydantic import BaseModel


class MessagesModel(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True