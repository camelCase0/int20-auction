from fastapi import FastAPI
from auth.auth import auth_backend, fastapi_users
from auth.schema import UserCreate, UserRead, UserUpdate
from chat.router import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from pages.router import router as page_router
from lot.router import router as lot_router

import ssl

app = FastAPI(title="Auction apps")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(page_router)
app.include_router(chat_router)
app.include_router(lot_router)

origins = ["http://localhost:8000/","https://localhost:8000/", "http://127.0.0.1:5500", "http://64.225.5.39:8080", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Accept","Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('../cert/cert.pem', keyfile='../cert/key.pem')