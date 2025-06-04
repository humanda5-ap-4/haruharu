from datetime import date as _date
import re
import requests
from sqlalchemy import text
from common.response import generate_response
from db import engine_db

# 📍 현재 위치 자동 추정 (IP 기반)
def get_location_from_ip():
    try:
        res = requests.get("https://ipinfo.io", timeout=3)
        data = res.json()
        city = data.get("city", "")
        region = data.get("region", "")
        print(f"[INFO] 사용자 위치 추정됨 → city: {city}, region: {region}")
        return city or region or "서울"
    except Exception as e:
        print(f"[WARN] IP 기반 위치 추정 실패: {e}")
        return "서울"

# ✅ SQL 유효성 검사 함수
def is_valid_sql(sql: str) -> bool:
    sql_check = sql.strip().lower()
    is_valid = sql_check.startswith("select") and "from festival_info" in sql_check
    print(f"[DEBUG] SQL 유효성 검사 → 유효한가?: {is_valid}")
    return is_valid

# ✅ fallback SQL 생성
def fallback_sql(today: str, user_location: str) -> str:
    print("[INFO] fallback_sql() 실행됨")
    query1 = f"""
    SELECT * FROM festival_info
    WHERE fin_date >= '{today}'
    ORDER BY start_date
    LIMIT 5
    """
    query2 = f"""
    SELECT * FROM festival_info
    WHERE (festival_loc LIKE '%{user_location}%' OR address_roads LIKE '%{user_location}%' OR address_land LIKE '%{user_location}%')
    AND fin_date >= '{today}'
    ORDER BY start_date
    LIMIT 5
    """
    print("[DEBUG] fallback SQL 1:", query1.strip())
    print("[DEBUG] fallback SQL 2:", query2.strip())
    return query1.strip() + ";\n" + query2.strip()

# 🧠 LLM용 SQL 프롬프트 템플릿
SQL_PROMPT_TEMPLATE = """
너는 SQL 쿼리만 생성하는 AI야.

❗❗ 절대 설명하지 마. 설명은 금지야. 쿼리만 출력해.
사용 테이블: festival_info
사용 가능한 컬럼:
- festival_name
- festival_loc
- start_date
- fin_date
- address_roads
- address_land

규칙:
- 날짜가 없으면 fin_date >= '{today}'
- 지역 언급이 있으면 festival_loc, address_roads, address_land에 LIKE 조건을 OR로 묶어야 함
- 항상 start_date 기준 ORDER BY 정렬, LIMIT 5

예시:
입력: 서울 축제정보 좀 알려줘  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%서울%' OR address_roads LIKE '%서울%' OR address_land LIKE '%서울%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

[입력]
{query}

[출력]
"""

# 🧠 추천 요약 프롬프트
RECOMMEND_PROMPT_TEMPLATE = """
{day} 기준으로 추천할 축제를 자연스럽게 2~3문장으로 소개해 주세요:
{festival_list}
"""

# 🧱 SQL 생성 함수 (LLM + fallback)
def generate_sql(query: str, today: str, user_location: str) -> str:
    prompt = SQL_PROMPT_TEMPLATE.format(query=query, today=today)
    print("[DEBUG] LLM 프롬프트 생성 완료\n", prompt)

    sql = generate_response(prompt).strip()
    print("[DEBUG] LLM 원본 응답:\n", sql)

    sql = re.sub(r"```sql|```", "", sql).strip().strip(";")
    print("[DEBUG] 전처리된 SQL:\n", sql)

    # 전국 단어 포함 시 무시
    if any(re.search(p, sql, re.IGNORECASE) for p in [
        r"LIKE\s+['\"]%?(전국|전체|전지역|모두)%?['\"]",
        r"festival_(loc|name)\s*=\s*['\"](전국|전체|전지역|모두)['\"]"
    ]):
        print("[INFO] 전국 관련 필터 감지됨 → fallback으로 전환")
        return fallback_sql(today, user_location)

    # 유효성 검사
    if not is_valid_sql(sql):
        print("[WARN] LLM SQL이 유효하지 않음 → fallback으로 대체")
        return fallback_sql(today, user_location)

    return sql

# 📋 추천 문장 생성
def generate_recommendation(rows: list, day: str) -> str:
    bullet = "\n".join(
        f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']})"
        for r in rows
    )
    prompt = RECOMMEND_PROMPT_TEMPLATE.format(day=day, festival_list=bullet)
    print("[DEBUG] 추천 요약 프롬프트:\n", prompt)
    return generate_response(prompt.strip())

# 🎯 메인 핸들러
def handle(query: str, entities: list) -> str:
    today = _date.today().isoformat()
    day = next((e.value for e in entities if e.type == "DATE"), today)
    user_location = get_location_from_ip()
    print(f"[DEBUG] 입력 쿼리: {query}")
    print(f"[DEBUG] 오늘 날짜: {today}, 추천 기준 날짜: {day}")
    print(f"[DEBUG] 사용자 위치: {user_location}")

    sql = generate_sql(query, today, user_location)
    print("[DEBUG] 최종 실행 SQL:\n", sql)

    try:
        with engine_db.connect() as conn:
            results = []
            for part in sql.split(";"):
                if part.strip():
                    print(f"[DEBUG] 실행 중인 쿼리:\n{part.strip()}")
                    result = conn.execute(text(part.strip())).mappings().fetchall()
                    results.extend(dict(r) for r in result)

        if not results:
            print("[INFO] DB 조회 결과 없음")
            return "[BOT] 조건에 맞는 축제가 없습니다."

        print(f"[DEBUG] 축제 결과 개수: {len(results)}")

        list_text = "\n".join(
            f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']}, {r.get('distance', '?')}km)"
            for r in results
        )
        summary = generate_recommendation(results[:5], day)
        return f"{list_text}\n\n[BOT 추천 (상위 5개 요약)]\n{summary}"

    except Exception as e:
        print(f"[ERROR] DB 처리 실패: {e}")
        return f"[ERROR] SQL 실행 실패: {e}"
