#무료게임 동작x -> 수정

from sqlalchemy import text
import re
from common.response import generate_response
from db import engine_db

# 🔷 SQL 프롬프트 템플릿 (LLM에 전달)
SQL_PROMPT_TEMPLATE = """
[스팀 게임 SQL 생성기]

사용자의 요청을 기반으로 SQL을 생성하세요. 아래 규칙을 반드시 따르세요.

[규칙]
- 반드시 SELECT 문만 출력하세요. 설명, 따옴표, 백틱, 코드블럭은 포함하지 마세요.
- 컬럼은 steam_discountedgames 테이블의 컬럼만 사용하세요:
  game_name, game_genre, start_date, game_price, discount_rate, discounted_price
- 할인 조건이 명시되지 않으면 discount_rate > 0 조건을 추가하세요.
- 가격 조건이 없으면 상위 할인순으로 정렬하세요.
- limit이 명시되지 않으면 LIMIT 5를 추가하세요.
- "무료" 또는 "0원" 요청이 포함되면 Free 조건을 추가하세요.
[입력]
{query}

[출력]
"""

# 🔷 추천 요약 프롬프트
RECOMMEND_PROMPT_TEMPLATE = """
할인 중인 스팀 게임 추천 리스트입니다:

{game_list}

위 게임들을 2~3문장으로 요약해 사용자에게 자연스럽게 추천해 주세요.
"""

# 🎯 메인 핸들러
def handle(query: str, entities: list) -> str:
    #return "[BOT] steam intent 응답 테스트"
    sql = generate_sql(query)

    if not sql.lower().startswith("select"):
        return f"[ERROR] 잘못된 SQL 응답입니다:\n{sql}"

    with engine_db.connect() as conn:
        try:
            result = conn.execute(text(sql)).mappings().fetchall()
            rows = [dict(r) for r in result]

            if not rows:
                return "[BOT] 조건에 맞는 할인 게임이 없습니다."

            list_text = "\n".join(
                f"- {r['game_name']} ({r['discount_rate']}% 할인 → ${r['discounted_price']})"
                for r in rows
            )
            summary = generate_summary(rows)
            return f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
        except Exception as e:
            return f"[ERROR] SQL 실행 실패: {e}"

# 🔧 LLM 기반 SQL 생성 함수
def generate_sql(query: str) -> str:
    prompt = SQL_PROMPT_TEMPLATE.format(query=query)
    sql = generate_response(prompt).strip()
    sql = re.sub(r"```sql|```", "", sql).strip().strip(";")

    # 보안 필터링 (필요시)
    allowed_columns = {"game_name", "game_genre", "start_date", "game_price", "discount_rate", "discounted_price"}
    used_columns = set(re.findall(r"game_\w+", sql))
    if used_columns - allowed_columns:
        return "SELECT game_name, discounted_price FROM steam_games WHERE discount_rate > 0 ORDER BY discount_rate DESC LIMIT 5"

    if "limit" not in sql.lower():
        sql += " LIMIT 5"

    return sql

# 📝 추천 요약 문장 생성
def generate_summary(rows: list) -> str:
    bullets = "\n".join(
        f"- {r['game_name']} (${r['discounted_price']}, {r['discount_rate']}% 할인)"
        for r in rows
    )
    prompt = RECOMMEND_PROMPT_TEMPLATE.format(game_list=bullets)
    return generate_response(prompt.strip())
