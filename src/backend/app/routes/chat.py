# backend/app/routes/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from common.nlu_engine import NLUEngine

from intents.stock import handle as handle_stock_intent
from intents.festival import handle as handle_festival
from intents.steam import handle as handle_steam_intent
from intents.l2m import handle as handle_lineage2_intent
from intents.common import handle as handle_common


#from intents import INTENT_HANDLER  # 기타 스팀, 주식, 리니지2 등도 import
#from intents import common # 예외처리
router = APIRouter()

INTENT_HANDLER = {
    "common": handle_common,        # added  17 ~ 22 
    "stock": handle_stock_intent, #
    "lineage2": handle_lineage2_intent,
    "l2m": handle_lineage2_intent,
    "steam": handle_steam_intent,           # 
    "festival": handle_festival
    }
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

    # 디버깅용 출력
    print(f"[DEBUG] Intent: {intent}")

    print(f"[DEBUG] Entities: {[e.__dict__ for e in entities]}")

    handler = INTENT_HANDLER.get(intent, handle_common)
    answer = handler(req.query, entities)
    return ChatResponse(
        intent=intent,
        entities=[e.__dict__ for e in entities],
        answer=answer
    )