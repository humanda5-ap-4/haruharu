# Intent 분류 및 Entity 추출
import re
import joblib
from sentence_transformers import SentenceTransformer
from common.entity import TransformerEntityMatcher
from pathlib import Path

NLU_DIR = Path(__file__).resolve().parents[1] / "nlu"

class NLUEngine:
    _vec = None
    _clf = None
    _matcher = None

    @classmethod
    def ensure_loaded(cls):
        if cls._vec is None or cls._clf is None:
            cls._vec = joblib.load(NLU_DIR / "intent_encoder.joblib")
            cls._clf = joblib.load(NLU_DIR / "intent_clf.joblib")
        if cls._matcher is None:
            cls._matcher = TransformerEntityMatcher()  # fine-tuned + huggingface 조합 NER 사용

    @classmethod
    def classify_intent(cls, text: str) -> str:
        """
        1) Steam 관련 패턴(연도/가격/할인/장르추천/무료)을 먼저 검사
           ('steam_query' intent로 분기)
        2) 그렇지 않으면, 기존 학습된 모델로 예측
        """
        cls.ensure_loaded()

        # ────────────────────────────────────────────────────────────────────────
        # Steam 관련 패턴 정규식
        steam_pattern = re.compile(
            r"(?:\d{4}년[에]?\s*출시한\s*게임|"                  # 예: "2024년 출시한 게임"
            r"(?:스팀(?:에서)?\s*)?[\w가-힣A-Za-z0-9\+\-\:\.\s]+가격|"  # 예: "Through the Woods 가격", "스팀에서 Potion island 가격"
            r"할인률이\s*\d+%|"                                  # 예: "할인률이 50%가 넘는 게임"
            r"[A-Za-z가-힣]+\s*게임\s*추천|"                         # 예: "adventure 게임 추천해줘"
            r"무료\s*게임)"                                      # 예: "무료 게임 알려줘"
        )
        if steam_pattern.search(text):
            return "steam_query"
        # ────────────────────────────────────────────────────────────────────────

        # 2) Steam 패턴이 아니면, 기존 모델로 intent 분류
        embedding = cls._vec.encode([text])
        return cls._clf.predict(embedding)[0]

    @classmethod
    def extract_entities(cls, text: str):
        cls.ensure_loaded()
        return cls._matcher.extract(text)
