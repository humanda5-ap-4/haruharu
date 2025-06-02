# backend/app/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from common.nlu_engine import NLUEngine
from intents import festival, stock, stock_api   # 기타 스팀, 주식, 리니지2 등도 import

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    intent: str
    entities: list
    answer: str

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    intent = NLUEngine.classify_intent(req.query)
    entities = NLUEngine.extract_entities(req.query)
    handler = {
        "festival_query": festival.handle,
        "외부활동": festival.handle,
        "주가": stock.handle,  # 주식 인텐트 등록
        "주식": stock.handle,
    }.get(intent, festival.handle)  # 기본 핸들러로 festival 임시지정
    answer = handler(req.query, entities)
    return ChatResponse(intent=intent, entities=[e.__dict__ for e in entities], answer=answer)


