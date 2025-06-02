# 클래스/NER
from dataclasses import dataclass
from typing import List
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import pathlib

@dataclass
class Entity:
    type: str
    value: str
    start: int
    end: int

class TransformerEntityMatcher:
    def __init__(self):
        BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
        CUSTOM_MODEL_PATH = BASE_DIR / "nlu" / "ner_model"

        # 범용 NER 모델 (HuggingFace)
        self.generic_pipe = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            tokenizer="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )

        # 커스텀 NER 모델 (학습된 금융 도메인 모델)
        custom_tokenizer = AutoTokenizer.from_pretrained(CUSTOM_MODEL_PATH)
        custom_model = AutoModelForTokenClassification.from_pretrained(CUSTOM_MODEL_PATH)
        self.custom_pipe = pipeline(
            "ner",
            model=custom_model,
            tokenizer=custom_tokenizer,
            aggregation_strategy="simple"
        )

    def extract(self, text: str) -> List[Entity]:
        # 두 모델 결과 병합
        stock_keywords = {"주가", "주식", "PER", "PBR", "상장"}

        if any(keyword in text for keyword in stock_keywords):
            results = self.custom_pipe(text)
        else:
            results = self.generic_pipe(text)

        # 중복 제거 (start, end, label 기준)
        seen = set()
        entities = []
        for e in results:
            key = (e["start"], e["end"], e["entity_group"])
            if key not in seen:
                seen.add(key)
                entities.append(Entity(
                    type=e["entity_group"],
                    value=e["word"],
                    start=e["start"],
                    end=e["end"]
                ))
        return entities
