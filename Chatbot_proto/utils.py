import pymysql

conn = pymysql.connect(
    host='localhost',
    user='chatuser',
    password='chatpass123!',
    database='chat_logs',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def save_log(user_input, response):
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO chat_logs (user_input, bot_response) VALUES (%s, %s)"
            cursor.execute(sql, (user_input, response))
        conn.commit()
    except Exception as e:
        print(f"Error saving log: {e}")
