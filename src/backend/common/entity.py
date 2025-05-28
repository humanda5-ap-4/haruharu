# 클래스/NER
from dataclasses import dataclass
from typing import List
from transformers import pipeline

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
