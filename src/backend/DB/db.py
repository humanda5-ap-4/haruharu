#DB연결 함수         - 전현준님
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://humanda5:humanda5@192.168.0.73:3306/chatbot"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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



