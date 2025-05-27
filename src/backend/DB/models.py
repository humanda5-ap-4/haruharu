#SQLAlchemy 테이블 정의      - 전현준님

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from DB.db import Base

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
