# create, read, update, delete       - 전현준님


from sqlalchemy.orm import Session
from DB.models import ChatLog

def save_chat(db: Session, user_input: str, bot_response: str):
    chat = ChatLog(user_input=user_input, bot_response=bot_response)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

# 최근 대화 기록 가져오기
def get_chats(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ChatLog).offset(skip).limit(limit).all()
