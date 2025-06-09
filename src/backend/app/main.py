# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import chat

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.middleware("http")
async def log_request(request: Request, call_next):
    body = await request.body()
    print("📦 요청 본문:", body.decode())
    response = await call_next(request)
    return response

app.include_router(chat.router)


@app.get("/")
@app.head("/")
async def root():
    return {"message": "Hello World"}
