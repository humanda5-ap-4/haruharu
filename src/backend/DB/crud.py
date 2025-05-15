# create, read, update, delete       - 전현준님



from db import get_db_connection

# create
def insert_chat_log(user_id, message):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO chat_log (user_id, message) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, message))
            conn.commit()
        except Exception as e:
            print("삽입 실패:", e)
        finally:
            conn.close()



# read
def get_chat_logs_by_user(user_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM chat_log WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print("조회 실패:", e)
            return []
        finally:
            conn.close()


# UPDATE
def update_chat_message(log_id, new_message):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE chat_log SET message = %s WHERE id = %s"
                cursor.execute(sql, (new_message, log_id))
            conn.commit()
        except Exception as e:
            print("수정 실패:", e)
        finally:
            conn.close()



# DELETE
def delete_chat_log(log_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM chat_log WHERE id = %s"
                cursor.execute(sql, (log_id,))
            conn.commit()
        except Exception as e:
            print("삭제 실패:", e)
        finally:
            conn.close()
