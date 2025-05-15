# my SQL 연결시 사용할 예정  주석처리
# from .DB.db import get_db_connection

# def search_by_category_and_name(category: str, name_query: str):
#     conn = get_db_connection()
#     if not conn:
#         return {"error": "DB 연결 실패"}

#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 SELECT festival_name, festival_loc, start_date, fin_date, distance 
#                 FROM festival_table 
#                 WHERE category = %s AND festival_name LIKE %s
#                 LIMIT 1
#             """
#             cursor.execute(sql, (category, f"%{name_query}%"))
#             row = cursor.fetchone()
#             if row:
#                 return {
#                     "festival_name": row.get("festival_name", ""),
#                     "festival_loc": row.get("festival_loc", ""),
#                     "start_date": row.get("start_date", ""),
#                     "fin_date": row.get("fin_date", ""),
#                     "distance": row.get("distance", "정보 없음"),
#                 }
#             else:
#                 return {"error": f"{category}에서 '{name_query}' 관련 정보를 찾을 수 없습니다."}
#     except Exception as e:
#         return {"error": f"쿼리 실행 실패: {e}"}
#     finally:
#         conn.close()
