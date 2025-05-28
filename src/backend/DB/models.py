#SQLAlchemy 테이블 정의      - 전현준님

from sqlalchemy import Column, Integer, String, Date, Float, BigInteger, DateTime
from sqlalchemy.sql import func
from DB.db import Base

class FestivalInfo(Base):
    __tablename__ = "festival_info"

    id = Column(Integer, primary_key=True, index=True)
    festival_name = Column(String(255), nullable=False)
    festival_loc = Column(String(255))
    start_date = Column(Date)
    fin_date = Column(Date)
    distance = Column(String(255))
    address_roads = Column(String(255))
    address_land = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)



class L2m(Base):
    __tablename__ = "l2m"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(255), nullable=False)
    server_name = Column(String(255))
    now_mi_nuit_price = Column(BigInteger)
    avg_unit_price = Column(BigInteger)
    keyword = Column(String(255))
    searched_at = Column(DateTime)


class SteamDiscountedGames(Base):
    __tablename__ = "steam_discountedgames"

    id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String(255), nullable=False)
    game_genre = Column(String(255))
    start_date = Column(String(255)) 
    game_price = Column(String(255))
    discount_rate = Column(Float)
    discounted_price = Column(String(255))



class StockInfo(Base):
    __tablename__ = "stock_info"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(255), nullable=False)
    stock_name = Column(String(255), nullable=False)
    price = Column(Float)
    diff = Column(Float)
    price_change = Column(Float)
    source_api = Column(String(255))