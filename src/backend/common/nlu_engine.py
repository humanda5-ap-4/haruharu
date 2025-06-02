#Intent 분류 및 Entity 추출
import joblib
from sentence_transformers import SentenceTransformer
from common.entity import TransformerEntityMatcher
from pathlib import Path

NLU_DIR = Path(__file__).resolve().parents[1] / "nlu"

class NLUEngine:
    _vec = _clf = _matcher = None

    @classmethod
    def ensure_loaded(cls):
        if cls._vec is None:
            cls._vec = joblib.load(NLU_DIR / "intent_encoder.joblib")
            cls._clf = joblib.load(NLU_DIR / "intent_clf.joblib")
            cls._matcher = TransformerEntityMatcher()
            cls._stock_matcher = StockEntityMatcher(NLU_DIR / "stock_code_mapping.json") # stock json

    @classmethod
    def classify_intent(cls, text: str) -> str:
        cls.ensure_loaded()
        embedding = cls._vec.encode([text])
        return cls._clf.predict(embedding)[0]

    @classmethod
    def extract_entities(cls, text: str):
        cls.ensure_loaded()

        entities = cls._transformer_matcher.extract(text)
        stock_entities = cls._stock_matcher.extract(text)

        #return cls._matcher.extract(text)
        return entities + stock_entities
