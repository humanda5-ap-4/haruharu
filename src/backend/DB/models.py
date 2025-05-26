#SQLAlchemy 테이블 정의      - 전현준님
from sqlalchemy import Column, Integer, String, Float
from DB.db import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"  # DB에 있는 테이블명과 맞춰주세요

    stock_code = Column(Integer, primary_key=True, index=True)
    stock_name = Column(String(50), index=True)
    price = Column(Float)
    diff = Column(Float)
    rate = Column(Float)
