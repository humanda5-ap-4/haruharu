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
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import torch.nn.functional as F
import json
import pickle

class HybridIntentClassifier:
    def __init__(self, sbert_model_path, kobert_model_path, intent_dataset_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # SBERT 초기화
        self.sbert = SentenceTransformer(sbert_model_path)

        # KoBERT 초기화
        self.kobert_tokenizer = BertTokenizer.from_pretrained(kobert_model_path)
        self.kobert_model = BertForSequenceClassification.from_pretrained(kobert_model_path)
        self.kobert_model.to(self.device)
        self.kobert_model.eval()

        # intent 샘플 불러오기
        with open(intent_dataset_path, "r", encoding="utf-8") as f:
            self.intent_data = json.load(f)

        self.intent_texts = {}
        for item in self.intent_data:
            self.intent_texts.setdefault(item["intent"], []).append(item["text"])

        # SBERT intent embedding
        self.intent_embeddings = {
            intent: self.sbert.encode(texts, convert_to_tensor=True)
            for intent, texts in self.intent_texts.items()
        }

        # intent label mapping
        self.label2intent = {i: intent for i, intent in enumerate(self.intent_embeddings.keys())}

    def predict(self, text, threshold=0.65):
        sbert_embedding = self.sbert.encode(text, convert_to_tensor=True)

        # 유사도 비교
        best_intent, best_score = None, -1
        for intent, embeddings in self.intent_embeddings.items():
            score = util.cos_sim(sbert_embedding, embeddings).max().item()
            if score > best_score:
                best_intent, best_score = intent, score

        if best_score >= threshold:
            return best_intent, "SBERT", best_score

        # SBERT 신뢰도 낮을 경우 → KoBERT
        tokens = self.kobert_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        with torch.no_grad():
            outputs = self.kobert_model(**tokens)
            probs = F.softmax(outputs.logits, dim=1)
            label = torch.argmax(probs, dim=1).item()
            confidence = probs[0][label].item()

        return self.label2intent[label], "KoBERT", confidence

clf = HybridIntentClassifier(
    sbert_model_path="snunlp/KR-SBERT-V40K-klueNLI-augSTS",
    kobert_model_path="monologg/kobert",
    intent_dataset_path="dataset/intent_dataset.json"
)

intent, model, score = clf.predict("요즘 서울에 무슨 행사 있어?")
print(f"예측 인텐트: {intent} (모델: {model}, 점수: {score:.4f})")
