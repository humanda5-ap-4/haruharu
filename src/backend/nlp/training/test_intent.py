"""
✅ 목표
intent_embeddings.pkl 파일을 로드

입력 문장을 SBERT로 임베딩

각 인텐트 임베딩과 코사인 유사도 계산

가장 유사한 인텐트를 출력
"""

# test_intent.py
from sentence_transformers import SentenceTransformer, util
import torch
import pickle
import json
import os

# 경로 설정
DATASET_PATH = "dataset/intent_dataset.json"
EMBEDDING_PATH = "intent_embeddings.pkl"
THRESHOLD = 0.60

# 모델 로드
print("📦 SBERT 모델 로딩 중...")
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")
# model = SentenceTransformer("jhgan/ko-sbert-sts")

# 임베딩 로드
print("📥 임베딩 캐시 로드 중...")
with open(EMBEDDING_PATH, "rb") as f:
    intent_embeddings = pickle.load(f)

# 🔧 학습 데이터 추가 함수
def add_to_dataset(text, intent):
    print(f"📚 학습 데이터 추가: '{text}' → {intent}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    dataset.append({"text": text, "intent": intent})

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

# 🔧 임베딩 갱신 함수
def rebuild_embeddings():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    intent_texts = {}
    for item in dataset:
        intent_texts.setdefault(item["intent"], []).append(item["text"])

    new_embeddings = {
        intent: model.encode(texts, convert_to_tensor=True).mean(dim=0, keepdim=True)
        for intent, texts in intent_texts.items()
    }

    with open(EMBEDDING_PATH, "wb") as f:
        pickle.dump(new_embeddings, f)

    print("✅ intent_embeddings.pkl 갱신 완료")

# 🔍 인텐트 예측 함수
def predict_intent(text, threshold=THRESHOLD):
    input_embedding = model.encode(text, convert_to_tensor=True)

    best_intent = None
    best_score = -1

    for intent, embeddings in intent_embeddings.items():
        score = util.cos_sim(input_embedding, embeddings).max().item()
        if score > best_score:
            best_intent = intent
            best_score = score

    if best_score >= threshold:
        return best_intent, best_score
    else:
        return "unknown", best_score

# ✅ 대화 루프
if __name__ == "__main__":
    print("\n🧠 인텐트 예측 챗봇 시작! ('exit' 입력 시 종료)\n")

    while True:
        user_input = input("👤 사용자: ").strip()
        
        if user_input.lower() in ("exit", "quit"):
            print("👋 챗봇을 종료합니다.")
            break

        intent, score = predict_intent(user_input)
        print(f"🤖 예측 인텐트: {intent} (유사도: {score:.4f})")

        # 예측이 unknown이고, 유사도는 어느 정도 되는 경우 → 학습 유도
        if intent == "unknown" and score >= 0.50:
            corrected = input(f"🤔 어떤 인텐트로 추가할까요? (엔터 건너뜀): ").strip()
            if corrected:
                add_to_dataset(user_input, corrected)
                rebuild_embeddings()

                # 변경된 임베딩 다시 불러오기
                with open(EMBEDDING_PATH, "rb") as f:
                    intent_embeddings = pickle.load(f)
