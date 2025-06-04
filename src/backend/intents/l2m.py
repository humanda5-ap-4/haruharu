# intents/l2m.py
from common.response import generate_response

PROMPT_TEMPLATE = """
리니지 관련 소식을 알려줘.
특히 {topic}에 대한 최근 업데이트나 유저 반응이 궁금해.
"""

def handle_lineage2_intent(query: str, entities: list) -> str:
    topic = next((e.value for e in entities if e.type in {"GAME", "EVENT"}), None)
    prompt = PROMPT_TEMPLATE.format(topic=topic or "리니지")
    return generate_response(prompt.strip())
