# services/stock_service.py
from sqlalchemy.orm import Session
from DB.models import Stock
from sqlalchemy import desc



def search_stock_by_name(db: Session, name: str):
    stock = db.query(Stock).filter(Stock.stock_name == name).first()
    if not stock:
        return {"error": "해당 종목을 찾을 수 없습니다."}
    return {
        "stock_code": stock.stock_code,
        "name": stock.stock_name,
        "price": f"{int(stock.price):,}원",
        "diff": stock.diff,
        "rate": f"{stock.rate:+.2f}%",
    }


def get_stock_with_max_diff(db: Session):
    stock = db.query(Stock).order_by(desc(Stock.diff)).first()
    if not stock:
        return {"error": "주식 정보를 찾을 수 없습니다."}
    return {
        "stock_code": stock.stock_code,
        "name": stock.stock_name,
        "price": f"{int(stock.price):,}원",
        "diff": stock.diff,
        "rate": f"{stock.rate:+.2f}%",
    }