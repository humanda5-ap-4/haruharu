# db.py
from dotenv import load_dotenv
load_dotenv()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_CONFIG = {
    "host": "192.168.0.73",
    "port": 3306,
    "user": "humanda5",
    "password": "humanda5",
    "database": "chatbot",
}

# DB 연결 URL
DATABASE_URL = (
    f"mysql+mysqldb://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

DB_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine_db = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine_db, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
