#matcher.py: 사용자 입력에서 의도(intent) 를 판별
"""
사용자 입력
   │
   ▼
[engine.py]
   ├──> IntentMatcher (matcher.py)
   ├──> EntityParser (parser.py)
   └──> DB 조회 (DB에서 공공데이터 가져오기)
         └──> 결과 응답 생성
         
"""