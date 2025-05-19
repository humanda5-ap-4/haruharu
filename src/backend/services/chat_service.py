from db.connection import get_connection

def save_chat_log(user_id: str, message: str, reply: str):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO chat_logs (user_id, message, reply) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user_id, message, reply))
        conn.commit()
        return True
    except Exception as e:
        print("대화저장 오류:", e)
        return False
    finally:
        cursor.close()
        conn.close()
