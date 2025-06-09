# db.py
from dotenv import load_dotenv
load_dotenv()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DB 연결 URL
DATABASE_URL = (
    f"mysql+mysqldb://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine_db = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine_db, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
