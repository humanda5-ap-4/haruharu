# intents/l2m_api.py

import os
import requests
from dotenv import load_dotenv

# .env에서 API 키 로딩
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("auth")

# ✅ 아이템 검색 API 호출
def get_item_price_info(item_name: str, server_id: int = None) -> dict:


    url = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "search_keyword": item_name,
        "sale": "true"  # 판매중 아닌 전체 검색
    }
    if server_id:  # 있는 경우만 포함
        params["server_id"] = server_id

    print(f"[DEBUG] API 요청 파라미터: {params}")
    print(f"[DEBUG] API 요청 헤더: {headers}")
    print(f"[DEBUG] 요청 URL: {url}")
    
    if server_id:
        params["server_id"] = server_id

    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        #print("[DEBUG] API 응답 원문:", res.json())
        return res.json()
    except requests.RequestException as e:
        print(f"[ERROR] API 호출 실패: {e}")
        return {}
