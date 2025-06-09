import pandas as pd
import joblib
import pathlib
import sys

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
from common.logger import get_logger
logger = get_logger("train")

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SPLIT_DIR = DATA_DIR / "splits"
NLU_DIR = BASE_DIR / "nlu"

def _check_file(p: pathlib.Path, hint: str = ""):
    if not p.exists():
        logger.error(f"파일 없음: {p}")
        if hint:
            logger.error(hint)
        sys.exit(1)

def preprocess_data(seed: int = 42):
    intent_json = DATA_DIR / "intent_dataset.json"
    _check_file(intent_json)
    df = pd.read_json(intent_json, encoding="utf-8")
    train, temp = train_test_split(df, test_size=0.2, random_state=seed)
    valid, test = train_test_split(temp, test_size=0.5, random_state=seed)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    train.to_json(SPLIT_DIR / "intent_train.json", orient="records", force_ascii=False)
    valid.to_json(SPLIT_DIR / "intent_valid.json", orient="records", force_ascii=False)
    test.to_json(SPLIT_DIR / "intent_test.json", orient="records", force_ascii=False)
    logger.info("[Preprocess] 완료")

def train_intent_model():
    train_json = SPLIT_DIR / "intent_train.json"
    _check_file(train_json)
    df = pd.read_json(train_json, encoding="utf-8")
    model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
    embeddings = model.encode(df.text.tolist(), show_progress_bar=True)
    clf = LogisticRegression(max_iter=1000).fit(embeddings, df.intent)
    NLU_DIR.mkdir(exist_ok=True)
    joblib.dump(model, NLU_DIR / "intent_encoder.joblib")
    joblib.dump(clf, NLU_DIR / "intent_clf.joblib")
    logger.info("[Train] Intent 모델 학습 완료")
