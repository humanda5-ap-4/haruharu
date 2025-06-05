from datetime import date as _date
import re
import requests
from sqlalchemy import text
from common.response import generate_response
from db import engine_db

# 해외에서 건너오는 region entity 정규화
SQL_PROMPT_TEMPLATE = """
너는 SQL 쿼리만 생성하는 AI야.

❗❗ 절대 설명하지 마. 쿼리만 출력해.
사용 테이블: festival_info  
사용 가능한 컬럼:
- festival_name
- festival_loc
- start_date
- fin_date
- address_roads
- address_land

규칙:
1. 사용자 쿼리에서 날짜가 명시되지 않은 경우엔 fin_date >= '{today}' 조건을 기본 적용해.
2. 지역명이 포함되어 있다면 '시', '군', '구' 등 접미사는 제거하고 핵심 지역명만 추출해서 LIKE 검색 조건에 써.
   예: '성남시' → '성남', '마포구' → '마포', '강릉군' → '강릉'
3. 지역명은 festival_loc, address_roads, address_land 컬럼에 대해 OR로 LIKE 검색해야 해.
4. 결과는 start_date 오름차순 정렬, LIMIT 5

❗ 조건에 맞는 축제가 없을 경우를 대비해,
5. 같은 지역명을 쓰되, **fin_date < '{today}'** 조건을 사용해서 과거에 종료된 축제 중 가장 최근 5개도 함께 뽑아.
6. 쿼리는 항상 2개를 순서대로 써줘 (최신 쿼리 → fallback 쿼리)

예시:

입력: 서울 축제정보 좀 알려줘  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%서울%' OR address_roads LIKE '%서울%' OR address_land LIKE '%서울%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 성남시에서 열리는 축제 알려줘  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%성남%' OR address_roads LIKE '%성남%' OR address_land LIKE '%성남%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 대구 축제 뭐 있어?  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%대구%' OR address_roads LIKE '%대구%' OR address_land LIKE '%대구%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 강릉군 축제 중에 끝난 거 알려줘  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%강릉%' OR address_roads LIKE '%강릉%' OR address_land LIKE '%강릉%') AND fin_date < '{today}' ORDER BY fin_date DESC LIMIT 5

입력: 부산에서 요즘 하는 축제 있어?  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%부산%' OR address_roads LIKE '%부산%' OR address_land LIKE '%부산%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 인천광역시 축제 보여줘  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%인천%' OR address_roads LIKE '%인천%' OR address_land LIKE '%인천%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 전주 끝난 축제 알려줘  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%전주%' OR address_roads LIKE '%전주%' OR address_land LIKE '%전주%') AND fin_date < '{today}' ORDER BY fin_date DESC LIMIT 5

입력: 안산시에서 최근 열린 축제  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%안산%' OR address_roads LIKE '%안산%' OR address_land LIKE '%안산%') AND fin_date < '{today}' ORDER BY fin_date DESC LIMIT 5

입력: 구미에서 하는 거 뭐 있지?  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%구미%' OR address_roads LIKE '%구미%' OR address_land LIKE '%구미%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 요즘 대전 축제 없나  
출력: SELECT * FROM festival_info WHERE (festival_loc LIKE '%대전%' OR address_roads LIKE '%대전%' OR address_land LIKE '%대전%') AND fin_date >= '{today}' ORDER BY start_date LIMIT 5

입력: 성남시에서 하는 축제 알려줘  
출력:  
```sql
SELECT * FROM festival_info  
WHERE (festival_loc LIKE '%성남%' OR address_roads LIKE '%성남%' OR address_land LIKE '%성남%')  
AND fin_date >= '{today}'  
ORDER BY start_date  
LIMIT 5;

SELECT * FROM festival_info  
WHERE (festival_loc LIKE '%성남%' OR address_roads LIKE '%성남%' OR address_land LIKE '%성남%')  
AND fin_date < '{today}'  
ORDER BY fin_date DESC  
LIMIT 5;

❗ 반드시 쿼리를 두 개 출력해:
1) 최신 축제 기준 (fin_date >= '{today}')
2) fallback: 같은 지역명으로 fin_date < '{today}' 조건, 종료된 축제 최신순

쿼리는 아래처럼 두 개의 SQL을 순서대로 출력해:
```sql
-- 최신 축제
SELECT ...

-- 종료된 축제
SELECT ...
python


[입력]
{query}

[출력]
"""

RECOMMEND_PROMPT_TEMPLATE = """
{day} 기준으로 추천할 축제를 자연스럽게 2~3문장으로 소개해 주세요:
{festival_list}
"""

def normalize_region_name(name: str) -> str:
    return re.sub(r"(시|군|구)$", "", name.strip('% '))

def extract_region_from_entities(entities: list) -> str:
    for e in entities:
        if e.type in ["LOCATION", "CITY", "GEO"]:
            return normalize_region_name(e.value)
    return ""

def get_location_from_ip():
    try:
        res = requests.get("https://ipinfo.io", timeout=3)
        data = res.json()
        return data.get("city") or data.get("region") or "서울"
    except:
        return "서울"

def extract_region_from_sql(sql: str) -> str:
    matches = re.findall(r"LIKE\s+'%([^%']+)%'", sql)
    return matches[0] if matches else ""

def is_valid_sql(sql: str) -> bool:
    sql_check = sql.strip().lower()
    return sql_check.startswith("select") and "from festival_info" in sql_check

def fallback_sql(today: str, user_location: str) -> str:
    region = normalize_region_name(user_location)
    return f"""
    SELECT * FROM festival_info
    WHERE (festival_loc LIKE '%{region}%' OR address_roads LIKE '%{region}%' OR address_land LIKE '%{region}%')
    AND fin_date >= '{today}'
    ORDER BY start_date
    LIMIT 5;

    SELECT * FROM festival_info
    WHERE (festival_loc LIKE '%{region}%' OR address_roads LIKE '%{region}%' OR address_land LIKE '%{region}%')
    AND fin_date < '{today}'
    ORDER BY fin_date DESC
    LIMIT 5;
    """.strip()

def generate_sql(query: str, today: str, user_location: str, entities: list) -> str:
    prompt = SQL_PROMPT_TEMPLATE.format(query=query, today=today)
    sql = generate_response(prompt).strip()
    sql = re.sub(r"```sql|```", "", sql).strip()

    # SQL 문장 분리: ';' + 줄바꿈 + 공백 등 고려
    sql_parts = re.split(r';\s*\n+', sql)
    sql_parts = [part.strip() for part in sql_parts if part.strip()]

    if len(sql_parts) == 1:
        region = extract_region_from_entities(entities) or user_location
        sql_parts.append(f"""
        SELECT * FROM festival_info
        WHERE (festival_loc LIKE '%{region}%' OR address_roads LIKE '%{region}%' OR address_land LIKE '%{region}%')
        AND fin_date < '{today}'
        ORDER BY fin_date DESC
        LIMIT 5
        """.strip())

    if not is_valid_sql(sql_parts[0]):
        return fallback_sql(today, user_location)

    return ";\n".join(sql_parts)

def generate_recommendation(rows: list, day: str) -> str:
    bullet = "\n".join(
        f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']})"
        for r in rows
    )
    prompt = RECOMMEND_PROMPT_TEMPLATE.format(day=day, festival_list=bullet)
    return generate_response(prompt.strip())

def handle(query: str, entities: list) -> str:
    today = _date.today().isoformat()
    day = next((e.value for e in entities if e.type == "DATE"), today)
    user_location = get_location_from_ip()

    sql = generate_sql(query, today, user_location, entities)

    try:
        results = []
        fallback_results = []
        queries = [part.strip() for part in sql.split(";") if part.strip()]

        with engine_db.connect() as conn:
            for i, q in enumerate(queries):
                result = conn.execute(text(q)).mappings().fetchall()
                if i == 0:
                    results.extend(dict(r) for r in result)
                else:
                    fallback_results.extend(dict(r) for r in result)

        if not results and fallback_results:
            summary = generate_recommendation(fallback_results[:5], day)
            list_text = "\n".join(
                f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']})"
                for r in fallback_results
            )
            return f"{list_text}\n\n[BOT 추천 (fallback)]\n{summary}"

        if not results:
            return "[BOT] 조건에 맞는 축제가 없습니다."

        list_text = "\n".join(
            f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']})"
            for r in results
        )
        summary = generate_recommendation(results[:5], day)
        return f"{list_text}\n\n[BOT 추천 (상위 5개 요약)]\n{summary}"

    except Exception as e:
        return f"[ERROR] SQL 실행 실패: {e}"