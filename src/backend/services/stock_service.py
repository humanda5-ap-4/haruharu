# services/stock_service.py

from DB.db import get_db
from sqlalchemy.orm import Session
from DB.models import Stock  

def handle_intent(intent_obj):
    intent = intent_obj["intent"]
    entities = intent_obj.get("entities", {})
    db: Session = next(get_db())

    if intent == "get_top_volume_stocks":
        results = db.query(Stock).order_by(Stock.volume.desc()).limit(10).all()
        return {"message": "\n".join([f"{s.name} ({s.symbol}) - 거래량: {s.volume}" for s in results])}
    
    elif intent == "get_stock_price":
        symbol = entities.get("symbol", "")
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if stock:
            return {"message": f"{stock.name} ({stock.symbol})의 현재 가격은 {stock.price}원입니다."}
        else:
            return {"message": f"{symbol}에 해당하는 주식을 찾을 수 없습니다."}
    
    else:
        return {"message": "알 수 없는 요청입니다."}
