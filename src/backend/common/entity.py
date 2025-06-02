# 클래스/NER
from dataclasses import dataclass
from typing import List
from transformers import pipeline
import json

@dataclass
class Entity:
    type: str
    value: str
    start: int
    end: int

class TransformerEntityMatcher:
    def __init__(self, model_name="dslim/bert-base-NER"):
        self._pipe = pipeline("ner", model=model_name, tokenizer=model_name, aggregation_strategy="simple")

    def extract(self, text: str) -> List[Entity]:
        return [
            Entity(type=e["entity_group"], value=e["word"], start=e["start"], end=e["end"])
            for e in self._pipe(text)
        ]




class StockEntityMatcher:
    def __init__(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            self.stock_names = list(json.load(f).keys())

    def extract(self, text: str) -> List[Entity]:
        entities = []
        for name in self.stock_names:
            if name in text:
                start = text.index(name)
                end = start + len(name)
                entities.append(Entity(type="종목명", value=name, start=start, end=end))
        return entities