from common.response import generate_response
from .stock_api import get_access_token, get_stock_info
from .stock_utils import get_stock_code_by_name

PROMPT_TEMPLATE = """
[{company} 관련 뉴스 요약]

- 최근 주가: {price}원
- 참고 뉴스나 이슈가 있다면 요약해서 전달해줘.
"""

def handle(query: str, entities: list) -> str:
    company = next((e.value for e in entities if e.type in {"ORG", "STOCK"}), None)

    if not company:
        prompt = "최근 주식 시장 전반의 동향과 이슈를 요약해줘."
        return generate_response(prompt)

    code = get_stock_code_by_name(company)
    if not code:
        return f"[BOT] '{company}'에 대한 주식 정보를 찾을 수 없어요."

    # 실시간 주가 호출
    token = get_access_token("APPKEY", "APPSECRET")
    info = get_stock_info(code, token)
    price = info.get("stck_prpr", "정보 없음")

    # 뉴스 + 주가 요약 프롬프트
    prompt = PROMPT_TEMPLATE.format(company=company, price=price)
    return generate_response(prompt.strip())
