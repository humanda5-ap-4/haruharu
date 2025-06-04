# intents/stock.py

uvicorn app.main:app --reload
from backend.intents.stock_utils import get_stock_code_by_name, get_name_by_stock_code
from backend.intents.stock_api import get_access_token, get_stock_info
from backend.common.response import generate_response


from backend.intents.stock_api import get_investor_trends


PROMPT_TEMPLATE = """
다음은 {company} ({code})에 대한 주가 정보입니다: 아래 숫자는 모두 1주 기준 원 단위입니다.
현재가는 무조건 1주 단위입니다. 주식 1개의 거래량만 알려주세요

💰 현재가: {price}원
📉 전일 대비: {diff}원
📊 등락률: {rate}%

📰 관련 뉴스 및 이슈가 있다면 간단히 정리해줘.
"""

INVESTOR_TREND_TEMPLATE = """
{company} ({code})의 {investor} 투자자 매매 동향입니다:
{trend}
"""


def handle_stock_intent(query: str, entities: list) -> str:
    # 1️⃣ ORG 또는 STOCK 타입에서 기업명 추출
    company = next((e.value for e in entities if e.type in {"ORG", "STOCK"}), None)

    if company:
        for suffix in [" 주식정보", " 정보", " 관련"]:
            if company.endswith(suffix):
                company = company.replace(suffix, "")
                break

    # 1-1️⃣ 투자자 유형 추출 (외국인, 기관, 개인)
    investor = None
    if "외국인" in query:
        investor = "외국인"
    elif "기관" in query:
        investor = "기관"
    elif "개인" in query:
        investor = "개인"

    if not company:
        # 엔티티가 없으면 전체 시장 동향 요약 요청
        prompt = "최근 주식 시장의 전반적인 동향과 주요 이슈를 요약해줘."
        return generate_response(prompt)

    # 2️⃣ 종목코드 조회
    code = get_stock_code_by_name(company)
    if not code:
        return f"[BOT] '{company}'에 대한 주식 정보를 찾을 수 없어요."

    # 투자자 동향 요청일 경우 별도 처리
    if investor:
        token = get_access_token()
        if not token:
            return "[BOT] 인증 토큰을 가져오지 못했어요. 나중에 다시 시도해 주세요."

        # 외국인, 기관, 개인 등 투자자 동향 데이터 조회 (직접 구현 필요)
        trend_data = get_investor_trends(code, token, investor)
        if not trend_data:
            return f"[BOT] '{company}'의 {investor} 투자자 동향 데이터를 조회할 수 없습니다."

        return generate_response(
            INVESTOR_TREND_TEMPLATE.format(
                company=company,
                code=code,
                investor=investor,
                trend=trend_data
            ).strip()
        )

    # 3️⃣ 토큰 획득 및 주가 조회
    token = get_access_token()
    if not token:
        return "[BOT] 인증 토큰을 가져오지 못했어요. 나중에 다시 시도해 주세요."

    info = get_stock_info(code, token)
    if not info:
        return f"[BOT] '{company}'의 주식 데이터를 조회할 수 없습니다."

    # 4️⃣ 값 추출
    price = info.get("stck_prpr", "정보 없음")
    diff = info.get("prdy_vrss", "정보 없음")
    rate = info.get("prdy_ctrt", "정보 없음")

    # 5️⃣ 요약 프롬프트 작성 (전체 값 전달)
    prompt = PROMPT_TEMPLATE.format(
        company=company,
        code=code,
        price=price,
        diff=diff,
        rate=rate
    )

    return generate_response(prompt.strip())