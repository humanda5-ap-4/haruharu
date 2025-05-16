# src/backend/nlp/train_intent_model.py
"""
목표: SBERT + HuggingFace KoBERT Fine-tuning

1단계: SBERT로 인텐트 추출 (Baseline)
유사도 기반 분류: 문장 임베딩 → 코사인 유사도 비교

학습 필요 없음 (데이터 적을 때 매우 효과적)

2단계: KoBERT Fine-tuning으로 성능 향상
인텐트 분류용 supervised fine-tuning

데이터 많아지면 딥러닝 전환 (transformers 사용)

1단계 - SBERT 유사도 기반 → 베이스라인 확보
2단계 - 데이터 늘어나면 KoBERT fine-tuning
3단계 - Entity 추출 / Context 모델 추가로 확장

목표: SBERT + KoBERT 결합 인텐트 분류
1차 분류는 빠른 SBERT 유사도 기반으로 수행하고,
**신뢰도(유사도 점수)**가 낮으면 KoBERT fine-tuned 모델로 보완.

[입력 문장]
     │
     ▼
[SBERT 임베딩]
     │
     ▼
[각 intent 대표문장과 유사도 계산]
     │
     ▼
[최고 유사도 + 유사도 점수]
     │
     ├─── High confidence (예: 0.75↑) → SBERT 결과 채택
     │
     └─── Low confidence → KoBERT 모델로 재분류
                          │
                          ▼
                     최종 인텐트 출력

"""
from sentence_transformers import SentenceTransformer, util
import json
import pickle
import torch

class SbertIntentClassifier:
    def __init__(self, sbert_model_path, intent_dataset_path, embedding_cache_path=None):
        self.model = SentenceTransformer(sbert_model_path)

        with open(intent_dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        self.intent_texts = {}
        for item in dataset:
            self.intent_texts.setdefault(item["intent"], []).append(item["text"])

        # 캐시된 임베딩이 있다면 불러오고, 없으면 새로 생성
        if embedding_cache_path and self._load_embeddings(embedding_cache_path):
            print("✅ 캐시된 임베딩 로드 완료")
        else:
            print("🔄 SBERT 임베딩 생성 중...")
            self.intent_embeddings = {
                intent: self.model.encode(texts, convert_to_tensor=True)
                for intent, texts in self.intent_texts.items()
            }
            if embedding_cache_path:
                with open(embedding_cache_path, "wb") as f:
                    pickle.dump(self.intent_embeddings, f)
                print(f"✅ 캐시 저장 완료: {embedding_cache_path}")

    def _load_embeddings(self, path):
        try:
            with open(path, "rb") as f:
                self.intent_embeddings = pickle.load(f)
            return True
        except FileNotFoundError:
            return False

    def predict(self, text, threshold=0.65):
        input_embedding = self.model.encode(text, convert_to_tensor=True)

        best_intent, best_score = None, -1
        for intent, embeddings in self.intent_embeddings.items():
            score = util.cos_sim(input_embedding, embeddings).max().item()
            if score > best_score:
                best_intent, best_score = intent, score

        if best_score >= threshold:
            return best_intent, best_score
        else:
            return "unknown", best_score

clf = SbertIntentClassifier(
    sbert_model_path="snunlp/KR-SBERT-V40K-klueNLI-augSTS",
    intent_dataset_path="dataset/intent_dataset.json",
    embedding_cache_path="intent_embeddings.pkl"
)

intent, score = clf.predict("요즘 서울에 무슨 행사 있어?")
print(f"예측 인텐트: {intent} (점수: {score:.4f})")
