from sqlalchemy.orm import Session
from DB.models import ChatLog

def save_chat_log(db: Session, user_id: str, message: str, reply: str):
    try:
        new_log = ChatLog(user_id=user_id, message=message, reply=reply)
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return True
    except Exception as e:
        print("대화 저장 오류:", e)
        db.rollback()
        return False
