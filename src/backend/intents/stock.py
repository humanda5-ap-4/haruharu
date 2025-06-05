# intents/stock.py

from backend.intents.stock_utils import get_stock_code_by_name, get_name_by_stock_code
from backend.intents.stock_api import get_access_token, get_stock_info, request_new_token
from backend.common.response import generate_response


#prompt 디버깅 모드#
PROMPT_TEMPLATE = """
다음은 {company} ({code})에 대한 주가 정보입니다: 아래 숫자는 모두 1주 기준 원 단위입니다.
현재가는 무조건 1주 단위입니다. 주식 1개의 거래량만 알려주세요

💰 현재가: {price}원
📉 전일 대비: {diff}원
📊 등락률: {rate}%

📰 관련 뉴스 및 이슈가 있다면 간단히 정리해줘.
"""


PROMPT_TEMPLATE_FOREIGN = """
다음은 {company} ({code})의 투자자 보유 관련 정보입니다:

외국인 보유율: {foreign_rate}%
기관 보유율: {institution_rate}%
현재가: {price}원

외국인과 기관의 최근 투자 흐름을 요약해서 알려줘.
"""




def refresh_token_message():
    token = request_new_token()
    if token:
        return "✅ 주식 API 토큰이 성공적으로 재발행 되었습니다."
    else:
        return "❌ 토큰 재발행에 실패했습니다. 나중에 다시 시도해 주세요."
    
# 🎯 메인 핸들러
def handle(query: str, entities: list) -> str:

    # 토큰 재발행 명령어 감지
    if "토큰 재발행" in query or "토큰 갱신" in query:
        return refresh_token_message()

    def merge_wordpieces(entities):
        merged = []
        buffer = ""

        for e in entities:
            if e.type in {"ORG", "STOCK"}:
                if e.value.startswith("##"):
                    buffer += e.value[2:]
                else:
                    if buffer:
                        merged.append(buffer)
                    buffer = e.value
        if buffer:
            merged.append(buffer)
        return merged
    
    # 1️⃣ ORG 또는 STOCK 타입에서 기업명 추출
    #company = next((e.value for e in entities if e.type in {"ORG", "STOCK"}), None)
    merged_entities = merge_wordpieces(entities)
    company = merged_entities[0] if merged_entities else None
    
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

        # 4️⃣ 값 추출
    price = info.get("stck_prpr", "정보 없음")
    diff = info.get("prdy_vrss", "정보 없음")
    rate = info.get("prdy_ctrt", "정보 없음")

 # 외국인, 기관 관련 문의 판단
    keywords = ["외국인", "기관", "보유율", "외인"]
    if any(k in query for k in keywords):
        foreign_rate = get_foreign_rate(code, token)
        institution_rate = get_institution_rate(code, token)

        prompt = PROMPT_TEMPLATE_FOREIGN.format(
            company=company,
            code=code,
            foreign_rate=foreign_rate,
            institution_rate=institution_rate,
            price=price,
        )
        return generate_response(prompt.strip())

    # print(f"\n📈 {company} ({code})")
    # print(f"💰 현재가: {price}원")
    # print(f"📉 전일 대비: {diff}원")
    # print(f"📊 등락률: {rate}%\n")

    # 5️⃣ 요약 프롬프트 작성 (전체 값 전달)
    prompt = PROMPT_TEMPLATE.format(
        company=company,
        code=code,
        price=price,
        diff=diff,
        rate=rate
    )

    return generate_response(prompt.strip())
