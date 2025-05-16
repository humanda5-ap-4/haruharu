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


"""