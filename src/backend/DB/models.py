#SQLAlchemy 테이블 정의      - 전현준님


from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatLog(Base):
    __tablename__ = 'chat_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ChatLog(id={self.id}, user_id='{self.user_id}', message='{self.message[:20]}...')>"
    
    