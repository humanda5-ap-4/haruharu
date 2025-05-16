# src/backend/nlp/train_intent_model.py
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

with open("intent_dataset.json", "r", encoding="utf-8") as f:
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
