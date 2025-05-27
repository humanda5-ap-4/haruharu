# create, read, update, delete       - 전현준님


from sqlalchemy.orm import Session
from DB.models import StockInfo, SteamDiscountedGames, L2m, FestivalInfo
from typing import List, Optional
from datetime import datetime, date


# 동네축제 
def get_festival_list(db: Session) -> List[FestivalInfo]:
    return db.query(FestivalInfo).all()

def get_festival_by_name(db: Session, name: str) -> FestivalInfo:
    return db.query(FestivalInfo).filter(FestivalInfo.festival_name == name).first()

def get_festivals_by_location(db: Session, location: str) -> List[FestivalInfo]:
    return db.query(FestivalInfo).filter(FestivalInfo.festival_loc == location).all()

def get_festivals_by_date_range(db: Session, start: date, end: date) -> List[FestivalInfo]:
    return db.query(FestivalInfo).filter(
        FestivalInfo.start_date >= start,
        FestivalInfo.fin_date <= end
    ).all()


# 린2M
def get_l2m_items(db: Session) -> List[L2m]:
    return db.query(L2m).all()

def get_l2m_by_item_name(db: Session, item_name: str) -> List[L2m]:
    return db.query(L2m).filter(L2m.item_name == item_name).all()

def get_l2m_latest_by_keyword(db: Session, keyword: str) -> List[L2m]:
    return db.query(L2m).filter(L2m.keyword == keyword).order_by(L2m.searched_at.desc()).all()

# 스팀

def get_all_steam_discounted_games(db: Session) -> List[SteamDiscountedGames]:
    return db.query(SteamDiscountedGames).all()

def get_steam_games_by_genre(db: Session, genre: str) -> List[SteamDiscountedGames]:
    return db.query(SteamDiscountedGames).filter(SteamDiscountedGames.game_genre == genre).all()

def get_steam_game_by_name(db: Session, game_name: str) -> SteamDiscountedGames:
    return db.query(SteamDiscountedGames).filter(SteamDiscountedGames.game_name == game_name).first()
# 주식 

def get_stock_by_code(db: Session, stock_code: str) -> Optional[StockInfo]:
    return db.query(StockInfo).filter(StockInfo.stock_code == stock_code).first()

def get_stock_by_name(db: Session, stock_name: str) -> Optional[StockInfo]:
    return db.query(StockInfo).filter(StockInfo.stock_name == stock_name).first()

def get_all_stocks(db: Session) -> List[StockInfo]:
    return db.query(StockInfo).all()


def get_stock_info_by_name(db, stock_name: str):
    query = "SELECT * FROM stock_info WHERE stock_name = %s"
    result = db.execute(query, (stock_name,))
    return result.fetchone()  # 또는 fetchall() 필요에 따라