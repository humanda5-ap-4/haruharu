# src/backend/main.py

from fastapi import FastAPI, Query, Body, Depends
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware
#from mock_engine import search_by_category_and_name
from DB.db import get_db

from pydantic import BaseModel


from services.stock_service import search_stock_by_name, get_stock_with_max_diff
from services.nlp_service import get_intent_and_entities



app = FastAPI()



class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str



# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 origin으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest = Body(...), db: Session = Depends(get_db)):
    intent_obj = get_intent_and_entities(req.message)

    # intent_obj 예: {"intent": "get_max_diff_stock", "entities": {...}}
    if intent_obj["intent"] == "get_max_diff_stock":
        stock_info = get_stock_with_max_diff(db)
        if "error" in stock_info:
            reply = stock_info["error"]
        else:
            reply = (f"변동폭이 가장 큰 주식은 {stock_info['name']}이며, "
                     f"가격은 {stock_info['price']}, 변동폭은 {stock_info['diff']} "
                     f"({stock_info['rate']}) 입니다.")
    elif intent_obj["intent"] == "search_stock":
        name = intent_obj["entities"].get("stock_name")
        stock_info = search_stock_by_name(db, name)
        if "error" in stock_info:
            reply = stock_info["error"]
        else:
            reply = (f"{stock_info['name']} 현재 가격은 {stock_info['price']}, "
                     f"변동폭은 {stock_info['diff']} ({stock_info['rate']}) 입니다.")
    else:
        reply = "죄송합니다, 이해하지 못했습니다."

    return ChatResponse(reply=reply)