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

✅ matcher.py: 시나리오 기반의 Intent 분류기 → Rule 기반 → ML 기반 (TF-IDF + KNN or 로지스틱 회귀)         
"""
"""
✅ 선택 가이드: KoBERT vs SBERT
항목	KoBERT + Classifier	SBERT + Cosine Similarity
학습 필요	✅ (파인튜닝 필요)	❌ (사전 학습 모델만으로도 사용 가능)
속도	느림 (파인튜닝/추론 느림)	빠름 (임베딩 후 유사도 계산)
추천 용도	정확한 intent label 예측	유사 문장 기반 추천 or intent retrieval
결론	정형 intent 분류에 강함	유연한 의미 검색에 강함
🔧 여기선 먼저 Sentence-BERT로 빠르게 해보고, KoBERT는 이후 fine-tuning 버전으로 넘어가는 걸 추천드립니다.

✅ 목표: SBERT 기반 intent 매칭

사용자 입력 → SBERT 임베딩 → 사전 정의된 intent 문장들과 cosine 유사도 비교 → 가장 유사한 intent 선택
pip install sentence-transformers
SBERT 결과가 만족스럽다면 KoBERT는 fine-tuning 프로젝트로 진행

"""
# src/backend/nlp/matcher.py
import pickle
import os

# 로딩
MODEL_PATH = "intent_model.pkl"
VEC_PATH = "tfidf_vectorizer.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(VEC_PATH, "rb") as f:
    vectorizer = pickle.load(f)

def match_intent(user_input: str) -> str:
    X_input = vectorizer.transform([user_input])
    pred = model.predict(X_input)
    return pred[0]

if __name__ == "__main__":
    while True:
        text = input("👤 사용자 입력: ")
        print("🎯 예측 Intent:", match_intent(text))
