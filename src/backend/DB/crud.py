# create, read, update, delete       - 전현준님


from sqlalchemy.orm import Session
from DB.models import ChatLog

def insert_chat_log(db: Session, user_id: str, message: str):
    new_log = ChatLog(user_id=user_id, message=message)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_chat_logs_by_user(db: Session, user_id: str):
    return db.query(ChatLog).filter(ChatLog.user_id == user_id).all()

def update_chat_message(db: Session, log_id: int, new_message: str):
    chat_log = db.query(ChatLog).filter(ChatLog.id == log_id).first()
    if chat_log:
        chat_log.message = new_message
        db.commit()
        db.refresh(chat_log)
        return chat_log
    return None

def delete_chat_log(db: Session, log_id: int):
    chat_log = db.query(ChatLog).filter(ChatLog.id == log_id).first()
    if chat_log:
        db.delete(chat_log)
        db.commit()
        return True
    return False
