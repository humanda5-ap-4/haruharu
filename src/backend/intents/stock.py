# intents/stock.py

from backend.intents.stock_utils import get_stock_code_by_name, get_name_by_stock_code
from backend.intents.stock_api import get_access_token, get_stock_info
from backend.common.response import generate_response



PROMPT_TEMPLATE = """
📈 {company} ({code}) 관련 요약

💰 현재가: {price}원
📉 전일 대비: {diff}원
📊 등락률: {rate}%

📰 관련 뉴스 및 이슈가 있다면 간단히 정리해줘.
"""

# 🎯 메인 핸들러
def handle(query: str, entities: list) -> str:
    # 1️⃣ ORG 또는 STOCK 타입에서 기업명 추출
    company = next((e.value for e in entities if e.type in {"ORG", "STOCK"}), None)

    if company:
        for suffix in [" 주식정보", " 정보", " 관련"]:
            if company.endswith(suffix):
                company = company.replace(suffix, "")
                break

    if not company:
        # 엔티티가 없으면 전체 시장 동향 요약 요청
        prompt = "최근 주식 시장의 전반적인 동향과 주요 이슈를 요약해줘."
        return generate_response(prompt)

    # 2️⃣ 종목코드 조회
    code = get_stock_code_by_name(company)
    if not code:
        return f"[BOT] '{company}'에 대한 주식 정보를 찾을 수 없어요."

    # 3️⃣ 토큰 획득 및 주가 조회
    token = get_access_token()
    if not token:
        return "[BOT] 인증 토큰을 가져오지 못했어요. 나중에 다시 시도해 주세요."

    info = get_stock_info(code, token)
    if not info:
        return f"[BOT] '{company}'의 주식 데이터를 조회할 수 없습니다."

    price = info.get("stck_prpr", "정보 없음")

    # 4️⃣ 요약 프롬프트 작성
    prompt = PROMPT_TEMPLATE.format(company=company, price=price)
    return generate_response(prompt.strip())
