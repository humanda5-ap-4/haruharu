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
- "무료" 또는 "0원" 요청이 포함되면 무료 게임 목록을 반환하세요.
[입력]
{query}

[출력]
"""

# 🔷 추천 요약 프롬프트
RECOMMEND_PROMPT_TEMPLATE = """
다음 게임 목록을 보고, 간단하게(1~2문장) 핵심 추천 이유만 작성해 주세요:

{game_list}
"""

def generate_sql(query: str) -> str:
    """
    LLM을 이용해 SQL을 생성한다.
    """
    prompt = SQL_PROMPT_TEMPLATE.format(query=query)
    sql = generate_response(prompt).strip()
    sql = re.sub(r"```sql|```", "", sql).strip().strip(";")

    # 보안 필터링: 사용된 컬럼이 반드시 허용된 컬럼이어야 함
    allowed_columns = {
        "game_name",
        "game_genre",
        "start_date",
        "game_price",
        "discount_rate",
        "discounted_price"
    }
    used_columns = set(re.findall(r"game_\w", sql))
    if used_columns - allowed_columns:
        return "SELECT game_name, discounted_price FROM steam_discountedgames WHERE discount_rate > 0 ORDER BY discount_rate DESC LIMIT 5"

    if "limit" not in sql.lower():
        sql = " LIMIT 5"

    return sql

def generate_summary(rows: list) -> str:
    """
    간단 추천 요약 문장 생성
    """
    bullets = "\n".join(
        f"- {r['game_name']} (${r['discounted_price']}, {r['discount_rate']}% 할인)"
        for r in rows
    )
    prompt = RECOMMEND_PROMPT_TEMPLATE.format(game_list=bullets)
    return generate_response(prompt.strip())

def handle(query: str, entities: list) -> str:
    """
    Steam 관련 패턴을 우선 처리한다. 
    - 연도별 출시 (“2024년 출시한 게임”) 
    - 연도+장르별 출시 (“2023년 출시한 RPG 게임”)
    - 연도+장르+할인 (“2024년에 출시된 action 장르 중 할인 중인 게임”)
    - 가격 조회 (“Through the Woods 가격 알려줘”, “스팀에서 Potion island 가격 알려줘” 등) 
    - 원래 가격 기준 (“원래 가격이 X달러 이상인 게임 중에서 할인 중인 게임”) 
    - “할인된 가격이 X$ 이하인 게임” 또는 “할인된 가격이 X$ 이하인 Y게임” 
    - “할인중인  장르” (예: “할인중인 adventure 게임 알려줘”) 
    - “할인중인 게임” 등 일반 할인중 게임 조회 
    - 할인률 조회 (“할인률이 50%가 넘는 게임” 등)
    - “X%이상 할인하는 Y 장르 게임” (예: “50%이상 할인하는 RPG 게임 알려줘”) 
    - 할인률장르 조회 (“할인률이 70%가 넘는 RPG 게임” 등) 
    - 장르 추천 (“adventure 게임 추천해줘”, “RPG 게임 추천해줘” 등) 
    - 무료 게임 조회 (“무료 게임 알려줘”) 
    이 중 하나라도 매칭되지 않으면 None을 반환해 다음 핸들러로 넘긴다.
    """
    # ─────────────────────────────────────────────────────────────────────────
    # 0) Steam 관련 패턴(연도/장르+연도/장르+할인/가격/원래가격/할인된가격이하/할인된가격이하+장르/
    #    할인중장르/할인중/할인/할인이상+장르/장르추천/무료 등) 매칭 여부 확인

    # “연도+장르+할인” 패턴 (예: “2024년에 출시된 action 장르 중 할인 중인 게임”)
    year_genre_discount_match = re.search(
        r"(\d{4})년[에]?\s*출시(?:된|한)\s*([A-Za-z가-힣]+)\s*장르\s*중\s*할인\s*중인\s*게임",
        query
    )

    # “연도+장르” 패턴 (예: “2023년 출시한 RPG 게임”)
    year_genre_match = re.search(
        r"(\d{4})년[에]?\s*출시(?:된|한)\s*([A-Za-z가-힣]+)\s*게임",
        query
    )

    # “연도만” 패턴
    year_match = re.search(
        r"(\d{4})년[에]?\s*출시(?:된|한)\s*게임",
        query
    )

    # “게임 가격 조회” 패턴
    price_match = re.search(
        r"(?:스팀(?:에서)?\s*)?([\w가-힣A-Za-z0-9\:\.\s\-]+)\s*가격",
        query
    )

    # “원래 가격이 X달러 이상인 게임” 패턴
    original_price_match = re.search(
        r"원래\s*가격이\s*(\d+)\s*달러\s*이상인\s*게임",
        query
    )

    # “할인된 가격이 X$ 이하인 게임” 패턴 (장르 없이)
    price_discounted_match = re.search(
        r"할인된\s*가격이\s*(\d+)\s*\$?\s*이하인\s*게임",
        query
    )

    # “할인된 가격이 X$ 이하인 Y게임” 패턴 (가격+장르)
    price_discounted_genre_match = re.search(
        r"할인된\s*가격이\s*(\d+)\s*\$?\s*이하인\s*([A-Za-z가-힣]+)게임",
        query
    )

    # “할인중인 + 장르” 패턴 (예: “할인중인 adventure 게임”)
    discount_genre_any_match = re.search(
        r"(?:할인중인|할인\s*하고\s*있는|현재\s*할인\s*중인|지금\s*할인중인)\s*([A-Za-z가-힣]+)\s*게임",
        query
    )

    # “할인중인 게임” (장르 없이)
    discount_any_match = re.search(
        r"(?:할인중인|할인\s*하고\s*있는|현재\s*할인\s*중인|지금\s*할인중인)\s*게임",
        query
    )

    # “할인률이 X%가 넘는 게임” (장르 없이)
    discount_only_match = re.search(
        r"할인률이\s*(\d+)%\s*가\s*넘는\s*게임",
        query
    )

    # “할인률이 X%가 넘는 Y 장르 게임” 패턴
    discount_genre_match = re.search(
        r"할인률이\s*(\d+)%\s*가\s*넘는\s*([A-Za-z가-힣]+)\s*게임",
        query
    )

    # “X%이상 할인하는 Y 장르 게임” 패턴
    discount_genre_atleast_match = re.search(
        r"(\d+)%이상\s*할인하는\s*([A-Za-z가-힣]+)\s*게임",
        query
    )

    # “장르 추천” 패턴 (예: “adventure 게임 추천해줘”)
    genre_recommend_match = re.search(
        r"([A-Za-z가-힣]+)\s*게임\s*추천",
        query
    )

    # “무료 게임” 패턴
    free_match = bool(re.search(r"무료\s*게임", query))

    # 0-1) 아무 패턴에도 매칭되지 않으면 None 반환
    if not (
        year_genre_discount_match
        or year_genre_match
        or year_match
        or price_match
        or original_price_match
        or price_discounted_match
        or price_discounted_genre_match
        or discount_genre_any_match
        or discount_any_match
        or discount_only_match
        or discount_genre_match
        or discount_genre_atleast_match
        or genre_recommend_match
        or free_match
    ):
        return None
    # ─────────────────────────────────────────────────────────────────────────

    # 1) “연도+장르+할인” 패턴 처리
    if year_genre_discount_match:
        year = year_genre_discount_match.group(1)
        requested_genre = year_genre_discount_match.group(2)
        sql = """
        SELECT
            game_name,
            game_genre,
            start_date,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE start_date LIKE :year_pattern
          AND LOWER(game_genre) LIKE LOWER(:genre_pattern)
          AND discount_rate > 0
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {
                        "year_pattern": f"%{year}%",
                        "genre_pattern": f"%{requested_genre}%"
                    }
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] {year}년에 출시된 '{requested_genre}' 장르 중 할인 중인 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}, 출시일: {r['start_date']}) "
                    f"- {r['discount_rate']}% 할인 → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] {year}년에 출시된 '{requested_genre}' 장르 중 할인 중인 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 연도+장르+할인 조회 실패: {e}"

    # 2) “연도+장르별 출시 게임 조회” 패턴 처리
    if year_genre_match:
        year = year_genre_match.group(1)
        requested_genre = year_genre_match.group(2)
        sql = """
        SELECT
            game_name,
            game_genre,
            start_date
        FROM steam_discountedgames
        WHERE start_date LIKE :year_pattern
          AND LOWER(game_genre) LIKE LOWER(:genre_pattern)
        ORDER BY start_date DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {
                        "year_pattern": f"%{year}%",
                        "genre_pattern": f"%{requested_genre}%"
                    }
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] {year}년에 출시된 '{requested_genre}' 장르 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}, 출시일: {r['start_date']})"
                    for r in rows
                )
                return f"[BOT] {year}년에 출시된 '{requested_genre}' 장르 게임 목록:\n{list_text}"
            except Exception as e:
                return f"[ERROR] 연도+장르별 출시 게임 조회 실패: {e}"

    # 3) “연도별 출시 게임 조회” 패턴 처리
    if year_match:
        year = year_match.group(1)
        year_sql = """
        SELECT
            game_name,
            game_genre,
            start_date
        FROM steam_discountedgames
        WHERE start_date LIKE :year_pattern
        ORDER BY start_date DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(year_sql),
                    {"year_pattern": f"%{year}%"}
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] {year}년에 출시된 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}, 출시일: {r['start_date']})"
                    for r in rows
                )
                return f"[BOT] {year}년에 출시된 게임 목록:\n{list_text}"
            except Exception as e:
                return f"[ERROR] 연도별 출시 게임 조회 실패: {e}"
            
    #“게임 가격 조회” 패턴 처리 (price_match 분기)
    if price_match:
        game_name = price_match.group(1).strip()
        sql = """
        SELECT
            game_name,
            game_genre,
            game_price,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE LOWER(game_name) LIKE LOWER(:name_pattern)
        LIMIT 1
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {"name_pattern": f"%{game_name}%"}
                ).mappings().fetchall()

                if not result:
                    return f"[BOT] '{game_name}' 게임 정보를 찾을 수 없습니다."

                r = dict(result[0])
                price = r.get("game_price")
                discount = r.get("discount_rate")
                discounted = r.get("discounted_price")

                price_text = f"${price}" if price is not None else "가격 정보 없음"
                discount_text = f"{discount}%" if discount is not None else "할인률 정보 없음"
                discounted_text = f"${discounted}" if discounted is not None else "할인가 정보 없음"

                return (
                    f"[BOT] '{r['game_name']}' 정보:\n"
                    f"- 장르: {r['game_genre']}\n"
                    f"- 원래 가격: {price_text}\n"
                    f"- 할인률: {discount_text}\n"
                    f"- 현재 가격: {discounted_text}"
                )
            except Exception as e:
                return f"[ERROR] 가격 조회 실패: {e}"

    # 4) “원래 가격이 X달러 이상인 게임 중에서 할인 중인 게임” 패턴 처리
    if original_price_match:
        threshold = int(original_price_match.group(1))
        sql = """
        SELECT
            game_name,
            game_genre,
            game_price,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE game_price >= :threshold
          AND discount_rate > 0
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {"threshold": threshold}
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] 원래 가격이 {threshold}달러 이상이면서 할인 중인 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - 원가 ${r['game_price']}, "
                    f"{r['discount_rate']}% 할인 → 할인된 가격 ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 원래 가격이 {threshold}달러 이상이면서 할인 중인 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 원래 가격 조건 조회 실패: {e}"

    # 5) “할인된 가격이 X$ 이하인 Y게임” 패턴 처리
    if price_discounted_genre_match:
        threshold = int(price_discounted_genre_match.group(1))
        requested_genre = price_discounted_genre_match.group(2)
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discounted_price <= :threshold
          AND LOWER(game_genre) LIKE LOWER(:genre_pattern)
        ORDER BY discount_rate DESC, discounted_price ASC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {
                        "threshold": threshold,
                        "genre_pattern": f"%{requested_genre}%"
                    }
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] 할인된 가격이 ${threshold} 이하인 '{requested_genre}' 장르 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% 할인 → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 할인된 가격이 ${threshold} 이하인 '{requested_genre}' 장르 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 가격+장르 조건 조회 실패: {e}"

    # 6) “할인된 가격이 X$ 이하인 게임” 패턴 처리
    if price_discounted_match:
        threshold = int(price_discounted_match.group(1))
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discounted_price <= :threshold
        ORDER BY discount_rate DESC, discounted_price ASC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {"threshold": threshold}
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] 할인된 가격이 ${threshold} 이하인 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% 할인 → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 할인된 가격이 ${threshold} 이하인 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 할인된 가격 이하인 게임 조회 실패: {e}"

    # 7) “할인중인 + 장르” 패턴 처리
    if discount_genre_any_match:
        requested_genre = discount_genre_any_match.group(1)
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discount_rate > 0
          AND LOWER(game_genre) LIKE LOWER(:genre_pattern)
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {"genre_pattern": f"%{requested_genre}%"}
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] '{requested_genre}' 장르에서 할인 중인 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] '{requested_genre}' 장르에서 할인 중인 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 할인 중인 장르별 게임 조회 실패: {e}"

    # 8) “할인중인 게임” 패턴 처리
    if discount_any_match:
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discount_rate > 0
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(text(sql)).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return "[BOT] 현재 할인 중인 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% 할인 → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 현재 할인 중인 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 할인 중인 게임 조회 실패: {e}"

    # 9) “X%이상 할인하는 Y 장르 게임” 패턴 처리
    if discount_genre_atleast_match:
        threshold = int(discount_genre_atleast_match.group(1))
        requested_genre = discount_genre_atleast_match.group(2)
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discount_rate >= :threshold
          AND LOWER(game_genre) LIKE LOWER(:genre_pattern)
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {
                        "threshold": threshold,
                        "genre_pattern": f"%{requested_genre}%"
                    }
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] 할인률이 {threshold}% 이상인 '{requested_genre}' 장르 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 할인률이 {threshold}% 이상인 '{requested_genre}' 장르 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 할인 이상 조건 장르별 게임 조회 실패: {e}"

    # 10) “할인률이 X%가 넘는 게임” (장르 없이) 패턴 처리
    if discount_only_match:
        threshold = int(discount_only_match.group(1))
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discount_rate > :threshold
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {"threshold": threshold}
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] 할인률이 {threshold}%가 넘는 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 할인률이 {threshold}%가 넘는 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 할인률만 조회 실패: {e}"

    # 11) “할인률이 X%가 넘는 Y 장르 게임” 패턴 처리
    if discount_genre_match:
        threshold = int(discount_genre_match.group(1))
        requested_genre = discount_genre_match.group(2)
        sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE discount_rate > :threshold
          AND LOWER(game_genre) LIKE LOWER(:genre_pattern)
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(sql),
                    {
                        "threshold": threshold,
                        "genre_pattern": f"%{requested_genre}%"
                    }
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] 할인률이 {threshold}%가 넘는 '{requested_genre}' 장르 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] 할인률이 {threshold}%가 넘는 '{requested_genre}' 장르 게임 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] 조건부 게임 조회 실패: {e}"

    # 12) “장르 추천” 패턴 처리 (예: “adventure 게임 추천해줘”)
    if genre_recommend_match:
        requested_genre = genre_recommend_match.group(1)
        genre_filter_sql = """
        SELECT
            game_name,
            game_genre,
            discount_rate,
            discounted_price
        FROM steam_discountedgames
        WHERE LOWER(game_genre) LIKE LOWER(:genre_pattern)
          AND discount_rate > 0
        ORDER BY discount_rate DESC
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(
                    text(genre_filter_sql),
                    {"genre_pattern": f"%{requested_genre}%"}
                ).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return f"[BOT] '{requested_genre}' 장르에서 할인 중인 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']}) - {r['discount_rate']}% → ${r['discounted_price']}"
                    for r in rows
                )
                summary = generate_summary(rows)
                return (
                    f"[BOT] '{requested_genre}'장르 할인 게임 추천 목록:\n"
                    f"{list_text}\n\n[BOT 추천 요약]\n{summary}"
                )
            except Exception as e:
                return f"[ERROR] '{requested_genre}' 장르 조회 실패: {e}"

    # 13) “무료 게임” 패턴 처리
    if free_match:
        free_sql = """
        SELECT
            game_name,
            game_genre
        FROM steam_discountedgames
        WHERE discounted_price = 0
        ORDER BY game_name
        LIMIT 10
        """
        with engine_db.connect() as conn:
            try:
                result = conn.execute(text(free_sql)).mappings().fetchall()
                rows = [dict(r) for r in result]

                if not rows:
                    return "[BOT] 현재 무료로 제공되는 게임을 찾을 수 없습니다."

                list_text = "\n".join(
                    f"- {r['game_name']} ({r['game_genre']})"
                    for r in rows
                )
                return f"[BOT] 현재 무료로 플레이 가능한 게임 목록:\n{list_text}"
            except Exception as e:
                return f"[ERROR] 무료 게임 조회 실패: {e}"

    # 14) “그 외” SQL 생성 로직 처리 (LLM 기반)
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
            return f"[BOT]\n{list_text}\n\n[BOT 추천 요약]\n{summary}"
        except Exception as e:
            return f"[ERROR] SQL 실행 실패: {e}"