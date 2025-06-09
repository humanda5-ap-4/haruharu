import os
import requests
from dotenv import load_dotenv

# ✅ .env에서 auth 토큰 불러오기
load_dotenv()
AUTH_TOKEN = os.getenv("auth")

# ✅ 리니지2M 마켓 검색 API
API_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"

# ✅ 전역 상태 (단일 사용자용)
last_item_name = None

# ✅ 아이템 검색 API 호출
def search_items(item_name: str) -> dict:
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    params = {
        "search_keyword": item_name,
        "sale": "false"
    }

    try:
        res = requests.get(API_URL, headers=headers, params=params)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"[❌ 오류] 상태 코드: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"[❌ 예외 발생]: {e}")

    return {}

# ✅ 서버명 비교 (부분 일치 허용 + "월드" 제거)
def find_item_in_response(response: dict, item_name: str, server_query: str) -> dict:
    normalized_query = server_query.replace("월드", "").strip()
    for item in response.get("contents", []):
        if item["item_name"] == item_name and normalized_query in item["server_name"]:
            return item
    return None

# ✅ 메인 챗봇 핸들러
def handle(query: str) -> str:
    global last_item_name

    query = query.strip()

    if "시세" in query:
        # 🎯 사용자: "xxx 시세 알려줘"
        item_name = query.replace("시세", "").replace("알려줘", "").strip()
        last_item_name = item_name
        return f"[BOT] '{item_name}'의 시세를 확인할 서버명을 알려주세요."

    elif last_item_name:
        # 🎯 사용자: 서버명 입력
        server_name = query
        response = search_items(last_item_name)

        if not response:
            return "[BOT] 아이템 검색 중 오류가 발생했습니다."

        result = find_item_in_response(response, last_item_name, server_name)

        if result:
            price = result.get("now_min_unit_price", 0)
            return f"[BOT] '{last_item_name}' ({result['server_name']})의 최저가는 {int(price):,} 아데나입니다."
        else:
            return f"[BOT] '{last_item_name}'의 '{server_name}' 서버 가격 정보를 찾을 수 없습니다."

    else:
        return "[BOT] 먼저 아이템명을 입력해 주세요. 예: '핸드 오브 카브리오 시세 알려줘'"

# ✅ 테스트 루프
if __name__ == "__main__":
    print("💬 리니지2M 경매장 봇 테스트 중입니다. 종료하려면 'exit' 입력.")
    while True:
        user_input = input("YOU > ").strip()
        if user_input.lower() == "exit":
            break
        reply = handle(user_input)
        print(reply)
