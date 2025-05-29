# intents/common.py
from common.response import generate_response

def handle(query: str, entities: list) -> str:
    prompt = f"""사용자가 다음과 같은 질문을 했어요:
"{query}"

이 요청은 아직 정의된 intent에 포함되어 있지 않습니다.
적절한 대화를 이어가며 자연스럽게 답변해주세요.
"""
    return generate_response(prompt)
