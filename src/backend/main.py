# src/backend/main.py
import sys
import asyncio
from mock_engine import search_stock_by_name  # 주식 검색 함수 import

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Query, Body, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from DB.db import get_db
from DB.crud import insert_chat_log
from services.chat_service import save_chat_log
from services.nlp_service import get_intent_and_entities
from services.stock_service import handle_intent
from mock_engine import search_by_category_and_name

import os

app = FastAPI()

# ⚙️ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌐 정적 파일 서빙
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")

# 📩 챗봇 요청
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest = Body(...), db: Session = Depends(get_db)):
    intent_obj = get_intent_and_entities(req.message)
    reply_data = handle_intent(intent_obj)
    reply = reply_data.get("message", str(reply_data))

    success = save_chat_log(db, req.user_id, req.message, reply)
    if not success:
        print("대화 저장 실패")

    return ChatResponse(reply=reply)


@app.get("/api/stock")
def stock_search(query: str = Query(...)):
    result = search_stock_by_name(query)
    if "error" in result:
        return {"error": result["error"]}
    return result


# 🔍 축제, 공연 등 검색
@app.get("/api/search")
def search(category: str = Query(...), query: str = Query(...)):
    if not query.strip():
        return {"error": "검색어를 입력해주세요."}
    result = search_by_category_and_name(category, query)
    return result
