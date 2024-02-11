import requests
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from auth.models import User
from lot.schemas import GetLot

router = APIRouter(
    tags=["Pages"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/")
def get_base_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from main import fastapi_users
current_user = fastapi_users.current_user()
@router.get("/chat/{lot_id}")
def get_chat_page(lot_id:int, request: Request, user: User = Depends(current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "lot_id":lot_id, "user_id":user.id})

