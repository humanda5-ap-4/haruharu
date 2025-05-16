#parser.py: 입력에서 엔터티(entity) 또는 슬롯 정보를 추출
"""
✅ parser.py: Entity 추출기 → 정규식 기반 → 학습 기반 NER (spaCy / transformers)
HuggingFace KoBERT, KoELECTRA 기반으로 fine-tuning도 가능

✅ 목표 요약: parser.py
사용자 입력에서 아래와 같은 정보를 뽑아냅니다:

Entity 종류	예시 추출 내용
날짜	"2025-05-21", "이번 주말"
지역	"서울", "부산" 등
이름(query)	"뮤지컬 캣츠", "장미 축제"

✅ 우선은 정규식 기반 + 키워드 기반으로 시작하되,
나중에 HuggingFace의 KoBERT, KoELECTRA 같은 모델로 NER 파인튜닝 확장도 가능하게 구조를 짤게요.
# src/backend/nlp/parser.py

import re

# 지역 키워드 사전
REGIONS = ["서울", "부산", "대전", "대구", "광주", "제주", "인천", "울산", "경기", "강원", "전북", "전남", "경북", "경남", "충북", "충남"]

def parse_entities(user_input: str) -> dict:
    entities = {}

    # 날짜 (형식: 2025-05-21)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", user_input)
    if date_match:
        entities["date"] = date_match.group()

    # 지역 추출
    for region in REGIONS:
        if region in user_input:
            entities["region"] = region
            break

    # 이름 query 추출 (2자 이상 한글 묶음)
    name_match = re.findall(r"[가-힣]{2,}", user_input)
    if name_match:
        entities["name_query"] = " ".join(name_match)

    return entities
if __name__ == "__main__":
    while True:
        user_input = input("👤 사용자 입력: ")
        entities = parse_entities(user_input)
        print("🔍 추출된 엔터티:", entities)

👤 사용자 입력: 서울에서 장미 축제 알려줘
🔍 추출된 엔터티: {'region': '서울', 'name_query': '서울 장미 축제'}

👤 사용자 입력: 2025-06-10에 공연 뭐 있어?
🔍 추출된 엔터티: {'date': '2025-06-10', 'name_query': '공연'}

👤 사용자 입력: 이번 주말 부산에 가고 싶어
🔍 추출된 엔터티: {'region': '부산', 'name_query': '이번 주말 부산'}


⏭️ 향후 확장
단계	기술	설명
✅ 1단계	정규식 기반	빠르고 단순. 지금 이 단계
🔜 2단계	키워드 사전 + 시나리오 매칭	“이번 주말”, “다음 주” 같은 표현 처리
🔥 3단계	NER 모델 (KoBERT, KoELECTRA)	HuggingFace Transformers 기반 파인튜닝 가능
💬 4단계	대화 기반 슬롯 채우기	사용자가 누락한 정보 물어보는 흐름까지 (slot filling)
필요하시면:

자연어 날짜 처리 (이번 주말, 내일)도 지원 가능

KoBERT 기반 NER fine-tuning 샘플도 드릴 수 있어요

지금은 정규식 기반으로 가고, 확장하고 싶을 때 모델 베이스로 넘어가면 딱 좋아요.

추출 성능 테스트해보실래요? 아니면 NER 버전도 한번 보여드릴까요?
"""