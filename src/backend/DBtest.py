# DBUtils.py

from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine, inspect

# MySQL-MySQLdb 드라이버(mysqlclient) 사용
# DBUtils.py 상단, load_dotenv() 바로 아래
print("▶️ ENV DB_USER =", os.getenv("DB_USER"))
print("▶️ ENV DB_PASSWORD =", os.getenv("DB_PASSWORD"))
print("▶️ ENV DB_HOST =", os.getenv("DB_HOST"))
print("▶️ ENV DB_NAME =", os.getenv("DB_NAME"))

DATABASE_URL = (
    f"mysql+mysqldb://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)
engine_db = create_engine(DATABASE_URL, echo=False)


def list_tables():
    """
    연결된 데이터베이스의 모든 테이블 이름을 리스트로 반환합니다.
    """
    inspector = inspect(engine_db)
    return inspector.get_table_names()


def get_columns(table_name: str):
    """
    지정한 테이블의 컬럼 정보를 반환합니다.
    각 컬럼은 dict 형태로 name, type, nullable, default 등을 포함합니다.
    """
    inspector = inspect(engine_db)
    return inspector.get_columns(table_name)


if __name__ == "__main__":
    # 테이블 목록 출력
    tables = list_tables()
    print("=== Tables in Database ===")
    for tbl in tables:
        print(f"- {tbl}")

    # 각 테이블 별 컬럼 스키마 출력
    print("\n=== Table Columns ===")
    for tbl in tables:
        cols = get_columns(tbl)
        print(f"\n[{tbl}]")
        for col in cols:
            name = col["name"]
            dtype = col["type"]
            nullable = col["nullable"]
            default = col.get("default", None)
            print(f"  • {name} | {dtype} | nullable={nullable} | default={default}")
