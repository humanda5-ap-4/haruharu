import ssl
import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# SSL 우회 Adapter 정의
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.options &= ~ssl.OP_NO_RENEGOTIATION  # SSL 오류 우회
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

# 세션에 어댑터 적용
session = requests.Session()
session.mount('https://', SSLAdapter())

API_URL = "🔗실제 API URL로 교체 필요"
HEADERS = {
    "Authorization": "Bearer 🔐YOUR_TOKEN"
}

all_items = []
page = 1
page_size = 50

while True:
    params = {"page": page, "size": page_size}
    res = session.get(API_URL, headers=HEADERS, params=params)

    if res.status_code != 200:
        print(f"❌ 실패 (page {page}): {res.status_code}")
        print(res.text)
        break

    data = res.json()
    contents = data.get("contents", [])

    if not contents:
        print("✅ 모든 아이템 수집 완료")
        break

    all_items.extend(contents)
    print(f"✔️ {len(contents)}개 아이템 수집 (page {page})")

    page += 1
    time.sleep(0.2)

with open("item_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
