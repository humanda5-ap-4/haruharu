import random
from intents import stock_api


def handle(query: str, entities: list):

    print("DEBUG: entities =", entities)
    if entities:
        print("DEBUG: first entity type =", type(entities[0]))
        print("DEBUG: first entity content =", entities[0])
    """
    query: 사용자가 입력한 전체 문장
    entities: [{ 'type': '종목명', 'value': '삼성전자' }, ...] 형태라고 가정
    """

    # 1) 종목명 추출
    stock_name = None
    for ent in entities:
        if ent.get("type") == "종목명":
            stock_name = ent.get("value")
            break

    if not stock_name:
        return "어떤 종목의 정보를 원하시는지 알려주세요."

    try:
        # 2) 토큰 불러오기
        token = stock_api.load_access_token()
        if not token:
            return "토큰 발급에 실패했습니다. 잠시 후 다시 시도해주세요."

        # 3) 주식 코드 맵 로드 (최초 1회만 해도 되므로 실제로는 캐싱 권장)
        # 여기선 간단하게 직접 불러옴
        stock_code_mapping = stock_api.load_stock_code_mapping(stock_api.CSV_PATH)

        # 4) 주식 정보 요청
        info = stock_api.get_stock_info_by_name(stock_name, token, stock_code_mapping)

        if not info:
            return f"{stock_name} 종목 정보를 찾을 수 없습니다."

        # 5) 결과 문자열 생성 (예시)
        price = info.get("price")
        diff = info.get("diff")
        rate = info.get("rate")
        answer = f"{stock_name} 현재가 {price}원, 전일 대비 {diff}원, 등락률 {rate}% 입니다."
        return answer

    except Exception as e:
        responses = [
            "주식 정보를 가져오는 중 문제가 발생했어요.",
            "죄송합니다, 지금은 주식 정보 조회가 어렵습니다.",
            "다시 한번 시도해 주세요, 잠시 문제가 있네요."
        ]
        return random.choice(responses)
