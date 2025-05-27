#DB연결 함수         - 전현준님
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = "humanda5"
DB_PASSWORD = "humanda5"
DB_HOST = "192.168.0.73"
DB_PORT = 3306
DB_NAME = "chatbot"

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



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



