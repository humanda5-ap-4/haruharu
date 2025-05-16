# src/backend/nlp/train_intent_model.py
"""
왜 LogisticRegression?
간단하고 빠름

분류 작업(의도 분류)에 매우 자주 쓰이는 고전 모델

나중에 KNN, SVM, XGBoost 또는 딥러닝으로도 확장 가능

❓ 추가 질문 생각해볼 만한 것
“TF-IDF 말고 다른 벡터화 방법은?” → BERT/SBERT

“로지스틱 말고 다른 모델은?” → KNN, LSTM, transformer 등

“데이터가 적으면?” → Rule 기반 + 샘플 확장

🧠 정리: 지금 이걸 추천드려요
용도	추천 모델
Intent 분류	✅ TF-IDF + LogisticRegression 또는 SBERT
Entity 추출	✅ 정규식 → spaCy/KoBERT (추후)
텍스트 유사도 기반 검색	✅ SBERT
문맥 + 의미 고려 분류	❌ 지금은 BERT fine-tuning은 무리 (데이터 부족)
장기적으로	✅ HuggingFace KoBERT fine-tuning (NER)

지금 제일 효율적인 건?	TF-IDF + LogisticRegression + SBERT (유사도 검색용)
나중에 데이터 많아지면?	그때 KoBERT, Transformer fine-tuning 가능

SBERT(Sentence-BERT)
🧪 SBERT 기반 의도 분류 흐름
각 intent당 대표 문장 5~10개 준비 (예: "서울에 축제 뭐 있어?")

사전 임베딩 저장

사용자 입력 → SBERT 임베딩

Cosine 유사도 비교 → 가장 유사한 intent 선택
"""


import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

with open("dataset/intent_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

texts = [item["text"] for item in dataset]
labels = [item["intent"] for item in dataset]

# 1. 벡터화
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# 2. 모델 학습
model = LogisticRegression()
model.fit(X, labels)

# 3. 저장
with open("intent_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Intent 모델 학습 및 저장 완료!")
