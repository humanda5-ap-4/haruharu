# src/backend/mock_engine.py

from datetime import datetime

# =============================
# 1. MOCK DATA
# =============================
mock_festival_data = [
    {
        "id": 1,
        "festival_name": "서울 장미 축제",
        "festival_loc": "서울 중랑구 중화체육공원",
        "start_date": "2025-05-20",
        "fin_date": "2025-05-26",
        "distance": "3.2km",
        "region": "서울",
        "source_api": "TourAPI 4.0"
    },
    {
        "id": 2,
        "festival_name": "부산 바다 축제",
        "festival_loc": "부산 해운대 해수욕장",
        "start_date": "2025-08-01",
        "fin_date": "2025-08-06",
        "distance": "7.8km",
        "region": "부산",
        "source_api": "KOPIS 축제정보API"
    }
]

mock_performance_data = [
    {
        "id": 101,
        "festival_name": "뮤지컬 캣츠",
        "festival_loc": "서울 예술의전당",
        "start_date": "2025-06-10",
        "fin_date": "2025-06-25",
        "distance": "4.1km",
        "region": "서울",
        "source_api": "KOPIS 공연API"
    }
]

mock_tourist_data = []
mock_food_data = []
mock_sports_data = []

# ✅ 주식 데이터 추가
mock_stock_data = [
    {
        "id": 201,
        "stock_name": "삼성전자",
        "price": "75,000원",
        "change": "+1.2%",
        "date": "2025-05-21",
        "source_api": "MOCK_STOCK_API"
    },
    {
        "id": 202,
        "stock_name": "카카오",
        "price": "41,500원",
        "change": "-0.4%",
        "date": "2025-05-21",
        "source_api": "MOCK_STOCK_API"
    }
]

# =============================
# 2. 카테고리 맵핑
# =============================
mock_data_map = {
    "축제": mock_festival_data,
    "공연": mock_performance_data,
    "관광지": mock_tourist_data,
    "음식": mock_food_data,
    "스포츠": mock_sports_data,
    "주식": mock_stock_data  # 
}

# =============================
# 3. NLP 응답 포맷 생성
# =============================
def format_nlp_response(data: dict):
    if "stock_name" in data:
        return {
            "stock_name": data.get("stock_name", ""),
            "price": data.get("price", ""),
            "change": data.get("change", ""),
            "date": data.get("date", "")
        }
    else:
        return {
            "festival_name": data.get("festival_name", ""),
            "festival_loc": data.get("festival_loc", ""),
            "start_date": data.get("start_date", ""),
            "fin_date": data.get("fin_date", ""),
            "distance": data.get("distance", "정보 없음")
        }

# =============================
# 4. 날짜 필터링
# =============================
def filter_by_date(data, target_date: str):
    return [
        item for item in data
        if item["start_date"] <= target_date <= item["fin_date"]
    ]

# =============================
# 5. 일반화된 검색 함수
# =============================
def search_by_category_and_name(category: str, name_query: str):
    if not name_query.strip():  # 빈 문자열 또는 공백만 있으면
        return {"error": "검색어를 입력해 주세요."}

    data = mock_data_map.get(category)
    if data is None:
        return {"error": f"지원하지 않는 카테고리입니다: {category}"}
    for item in data:
        if category == "주식":
            if name_query in item.get("stock_name", ""):
                return {
                    "stock_name": item.get("stock_name", ""),
                    "stock_price": item.get("stock_price", ""),
                    "change": item.get("change", ""),
                    "volume": item.get("volume", "")
                }
        else:
            if name_query in item.get("festival_name", ""):
                return format_nlp_response(item)
    return {"error": f"{category}에서 '{name_query}' 관련 정보를 찾을 수 없습니다."}

# =============================
# 6. 테스트 실행
# =============================
if __name__ == "__main__":
    print("[카테고리별 이름 검색] '축제', '서울 장미 축제'")
    print(search_by_category_and_name("축제", "서울 장미 축제"))

    print("\n[카테고리별 이름 검색] '공연', '뮤지컬'")
    print(search_by_category_and_name("공연", "뮤지컬"))

    print("\n[카테고리별 이름 검색] '주식', '삼성전자'")
    print(search_by_category_and_name("주식", "삼성전자"))

    print("\n[오늘 기준 진행 중인 축제]")
    today = datetime.now().strftime("%Y-%m-%d")
    ongoing = filter_by_date(mock_festival_data, today)
    for item in ongoing:
        print(format_nlp_response(item))

def search_stock_by_name(name: str):
    fake_stock_data = {
        "삼성전자": {
            "name": "삼성전자",
            "price": "82,000원",
            "change": "+0.45%",
            "time": "2025-05-21 10:00"
        },
        "카카오": {
            "name": "카카오",
            "price": "57,200원",
            "change": "-1.20%",
            "time": "2025-05-21 10:00"
        }
    }
    return fake_stock_data.get(name, {"error": "해당 종목을 찾을 수 없습니다."})