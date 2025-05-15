#DB연결 함수         - 전현준님


import pymysql

def get_db_connection():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='chatuser',
            password='chatpass123!',
            database='chat_logs',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"DB 연결 실패: {e}")
        return None

