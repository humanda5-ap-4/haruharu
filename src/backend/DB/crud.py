# create, read, update, delete       - 전현준님
# src/backend/DB/crud.py
from .db import get_connection

def insert_event(event: dict, category: str):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO event_data (
        id, category, festival_name, festival_loc,
        start_date, fin_date, distance, region, source_api
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        event["id"], category, event["festival_name"], event["festival_loc"],
        event["start_date"], event["fin_date"], event["distance"],
        event["region"], event["source_api"]
    )

    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
