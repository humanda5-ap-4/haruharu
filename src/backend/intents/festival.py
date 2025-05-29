from datetime import date as _date
import re
from sqlalchemy import text
from common.response import generate_response
from db import engine_db

# 🧠 프롬프트 템플릿 (LLM용)
SQL_PROMPT_TEMPLATE = """
[규칙 기반 SQL 생성기]

당신은 사용자 요청을 SQL 쿼리로 바꾸는 AI입니다. 아래 규칙을 반드시 지켜야 합니다.

[규칙]
- '전국', '전지역', '전체', '모두'는 WHERE 조건에 포함하지 마세요.
- festival_name LIKE '%전국%' 또는 festival_loc = '전국' 등은 금지입니다.
- 날짜가 명시되지 않으면 fin_date >= '{today}' 조건을 기본으로 추가하세요.
- 반드시 SELECT 문만 출력하세요. 설명, 따옴표, 백틱, 코드블럭(```sql)은 포함하지 마세요.
- 컬럼은 festival_info 테이블의 컬럼만 사용하세요: festival_name, festival_loc, start_date, fin_date, distance

[입력]
{query}

[출력]
"""

RECOMMEND_PROMPT_TEMPLATE = """
{day} 기준으로 추천할 축제를 자연스럽게 2~3문장으로 소개해 주세요:
{festival_list}
"""

# 🎯 메인 핸들러
def handle(query: str, entities: list) -> str:
    today = _date.today().isoformat()
    day = next((e.value for e in entities if e.type == "DATE"), today)
    sql = generate_sql(query, today)

    if not sql.lower().startswith("select"):
        return sql

    with engine_db.connect() as conn:
        try:
            result = conn.execute(text(sql)).mappings().fetchall()
            rows = [dict(row) for row in result]
            if not rows:
                return "[BOT] 조건에 맞는 축제가 없습니다."

            list_text = "\n".join(
                f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']}, {r['distance']}km)"
                for r in rows
            )
            summary = generate_recommendation(rows[:5], day)
            return f"{list_text}\n\n[BOT 추천 (상위 5개 요약)]\n{summary}"
        except Exception as e:
            return f"[ERROR] SQL 실행 실패: {e}"

# 🧱 SQL 생성 함수
def generate_sql(query: str, today: str) -> str:
    prompt = SQL_PROMPT_TEMPLATE.format(query=query, today=today)
    sql = generate_response(prompt).strip()
    sql = re.sub(r"```sql|```", "", sql).strip().strip(";")

    # 유효성 검사
    if any(re.search(p, sql, re.IGNORECASE) for p in [
        r"LIKE\s+['\"]%?(전국|전체|전지역|모두)%?['\"]",
        r"festival_(loc|name)\s*=\s*['\"](전국|전체|전지역|모두)['\"]"
    ]):
        return f"SELECT * FROM festival_info WHERE fin_date >= '{today}' ORDER BY start_date LIMIT 5"

    if "limit" not in sql.lower():
        sql += " LIMIT 5"
    return sql

# 📋 추천 문장 생성
def generate_recommendation(rows: list, day: str) -> str:
    bullet = "\n".join(
        f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']})"
        for r in rows
    )
    prompt = RECOMMEND_PROMPT_TEMPLATE.format(day=day, festival_list=bullet)
    return generate_response(prompt.strip())
