from common.response import generate_response

PROMPT_TEMPLATE = "{keyword}에 대한 주식 시장 동향과 최근 뉴스를 요약해줘."

def handle(query: str, entities: list) -> str:
    keyword = next((e.value for e in entities if e.type in {"ORG", "STOCK"}), None)
    prompt = PROMPT_TEMPLATE.format(keyword=keyword or "주식 시장")
    return generate_response(prompt)