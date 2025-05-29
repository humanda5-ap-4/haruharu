# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,  # React 앱 주소
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
