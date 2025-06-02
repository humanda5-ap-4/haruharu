# backend/app/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from common.nlu_engine import NLUEngine
from intents import festival, stock  # 필요 시 다른 인텐트도 import

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
        "주가": stock.handle,
        "주식": stock.handle,
    }.get(intent, festival.handle)
    answer = handler(req.query, entities)
    return ChatResponse(intent=intent, entities=entities, answer=answer)
