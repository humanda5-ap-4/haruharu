
def extract_name(message: str, category: str) -> str:
    """
    사용자의 메시지에서 카테고리 단어를 제거한 뒤 남은 내용을 이름(Query)으로 간주
    """
    cleaned = message.replace("알려줘", "").replace("찾아줘", "").replace("검색해줘", "")
    cleaned = cleaned.replace(category, "").strip()
    return cleaned



def get_intent_and_entities(message: str):
    categories = ["축제", "공연", "관광지", "음식", "스포츠","주식"]
    for cat in categories:
        if cat in message:
            return {"intent": "검색", "category": cat, "name": extract_name(message, cat)}
