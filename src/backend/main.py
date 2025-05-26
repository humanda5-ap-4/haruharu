# src/backend/main.py
# 에러제거용 ----  
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#--------
from fastapi import FastAPI, Query, Body # Body Check Json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mock_engine import search_by_category_and_name


from pydantic import BaseModel #챗 저장
from services.chat_service import save_chat_log #챗 저장

import os

app = FastAPI()



frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 origin으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest = Body(...)):
    # 실제 챗봇은 아니지만, 임시 응답
    reply = f"[Mock 응답] '{req.message}'에 대한 응답입니다."
    
    # 대화 내용 저장
    success = save_chat_log(req.user_id, req.message, reply)
    if not success:
        print("⚠️ 대화 저장 실패")
    
    return ChatResponse(reply=reply)



@app.get("/api/search")
def search(category: str = Query(...), query: str = Query(...)):
    result = search_by_category_and_name(category, query)
    return result


app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
