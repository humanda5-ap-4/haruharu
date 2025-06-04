# backend/app/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from common.nlu_engine import NLUEngine
from intents import common # 예외처리

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
    handler = INTENT_HANDLER.get(intent, common.handle)  # 예외처리
    answer = handler(req.query, entities)
    return ChatResponse(
        intent=intent,
        entities=[e.__dict__ for e in entities],
        answer=answer
    )
