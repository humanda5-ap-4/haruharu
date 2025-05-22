#DB연결 함수         - 전현준님

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://chatuser:chatpass123!@localhost:3306/chat_logs?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

###/ 
# 
# import mysql.connector
# from mysql.connector import Error
#
#def get_db_connection():
#    try:
#        connection = mysql.connector.connect(
#            host='localhost',
#            user='chatuser',
#            password='chatpass123!',
#            database='chat_logs',
#            charset='utf8mb4',
#            cursorclass=pymysql.cursors.DictCursor
#        )
#        return connection
#    except Exception as e:
#        print(f"DB 연결 실패: {e}")
#        return None



