# 클래스/NER
from dataclasses import dataclass
from typing import List
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import pathlib
from typing import List, Dict

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
        # 주제별 키워드 기반 모델 선택
        stock_keywords = {"주가", "주식", "PER", "PBR", "상장", "코스피", "코스닥"}
        l2m_keywords = {"서버", "시세", "강화", "장비", "무기", "방어구", "세트", "아이템", "전설", "영웅", "희귀"}

        # 어떤 모델을 쓸지 결정
        if any(kw in text for kw in stock_keywords.union(l2m_keywords)):
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
    def extract_for_intent(self, text: str) -> List[Dict[str, str]]:
        entities = self.extract(text)
        # handle_stock_intent가 기대하는 dict 리스트 형태로 변환
        return [{"type": e.type, "value": e.value} for e in entities]
    


# ITEM_KEYWORDS = ["진명황의 집행검", "데스 나이트 소드", "엘븐 소드", "핸드 오브 카브리오", "제왕의 집행검", "마검 발록", "사신의 장궁", "마력의 단검", "신성한 장검", "크로노스의 지팡이", "마력의 지팡이", "카브리오의 양손검", "용사의 장검", "투사의 크로우", "다크 엘븐 보우", "진노의 도끼", "영웅의 활", "혈검 아수라", "지배자의 활", "비전의 지팡이"]

# def keyword_entity_matcher(text: str):
#     entities = []
#     for item in ITEM_KEYWORDS:
#         if item in text:
#             start = text.index(item)
#             entities.append(Entity(type="ITEM", value=item, start=start, end=start + len(item)))
#     return entities
