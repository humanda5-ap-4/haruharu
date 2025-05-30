# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat

from dotenv import load_dotenv
load_dotenv() 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

"""
react 연동
"""
# const res = await fetch("http://localhost:8000/chat", {
#   method: "POST",
#   headers: { "Content-Type": "application/json" },
#   body: JSON.stringify({ query: "이번 주말 축제 알려줘" }),
# });
# const data = await res.json();
# console.log(data.answer);
