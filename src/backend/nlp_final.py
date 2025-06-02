# 변경된 Intent 분류 및 Entity 추출 통합 코드
import argparse
import json
import pathlib
import re
import os
import sys
import logging
from dataclasses import dataclass
from datetime import date as _date
from typing import List, Optional

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer

from sqlalchemy import text
from db import engine_db

import ollama
from transformers import pipeline


# 경로 설정
BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SPLIT_DIR = DATA_DIR / "splits"
NLU_DIR = BASE_DIR / "nlu"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GLOBAL_KEYWORDS = {"전국", "전체", "모두", "전지역"}

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
        return [Entity(type=e["entity_group"], value=e["word"], start=e["start"], end=e["end"]) for e in self._pipe(text)]

class NLUEngine:
    _vec = _clf = _matcher = None

    @classmethod
    def ensure_loaded(cls):
        if cls._vec is None:
            cls._vec = joblib.load(NLU_DIR / "intent_encoder.joblib")
            cls._clf = joblib.load(NLU_DIR / "intent_clf.joblib")
            cls._matcher = TransformerEntityMatcher()

    @classmethod
    def classify_intent(cls, text: str) -> str:
        cls.ensure_loaded()
        embedding = cls._vec.encode([text])
        return cls._clf.predict(embedding)[0]

    @classmethod
    def extract_entities(cls, text: str) -> List[Entity]:
        cls.ensure_loaded()
        return cls._matcher.extract(text)

    @classmethod
    def answer(cls, query: str) -> str:
        intent = cls.classify_intent(query)
        logger.info(f"[INTENT 분류 결과] {intent}")
        ents = cls.extract_entities(query)

        if intent in {"festival_query", "외부활동"}:
            day = next((e.value for e in ents if e.type == "DATE"), _date.today().isoformat())
            sql = generate_sql(query)
            logger.info(f"[SQL 생성] {sql}")
            if not sql.lower().startswith("select"):
                return sql
            with engine_db.connect() as conn:
                try:
                    result = conn.execute(text(sql)).mappings().fetchall()
                    rows = [dict(row) for row in result]
                    if not rows:
                        return "[BOT] 조건에 맞는 축제가 없습니다."

                    list_text = "\n".join(
                        f"- {r['festival_name']} @ {r['festival_loc']} ({r['start_date']}~{r['fin_date']}, {r['distance']}km)"
                        for r in rows
                    )
                    summary = generate_recommendation_by_intent(intent, rows[:5], day)
                    return f"{list_text}\n\n[BOT 추천 (상위 5개 요약)]\n{summary}"
                except Exception as e:
                    return f"[ERROR] SQL 실행 실패: {e}"
        return generate_response(f"한국어 챗봇입니다. 다음 요청에 답하세요: {query}")

def generate_response(prompt: str) -> str:
    try:
        response = ollama.chat(model="gemma:2b", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        return f"[ERROR] Ollama 응답 실패: {e}"

def generate_sql(user_input: str) -> str:
    today = _date.today().isoformat()
    prompt = f"""
[규칙 기반 SQL 생성기]

당신은 사용자 요청을 SQL 쿼리로 바꾸는 AI입니다. 아래 규칙을 반드시 지켜야 합니다.

[규칙]
- '전국', '전지역', '전체', '모두'는 WHERE 조건에 포함하지 마세요.
- festival_name LIKE '%전국%' 또는 festival_loc = '전국' 등은 금지입니다.
- 날짜가 명시되지 않으면 fin_date >= '{today}' 조건을 기본으로 추가하세요.
- 반드시 SELECT 문만 출력하세요. 설명, 따옴표, 백틱, 코드블럭(```sql)은 포함하지 마세요.
- 컬럼은 festival_info 테이블의 컬럼만 사용하세요: festival_name, festival_loc, start_date, fin_date, distance

[입력]
{user_input}

[출력]
"""
    sql = generate_response(prompt).strip()

    # 코드블럭 제거
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.endswith("```"):
        sql = sql[:-3]
    sql = sql.strip().strip(";")

    # 금지 조건 체크
    forbidden_patterns = [
        re.compile(r"LIKE\s+['\"]%?(전국|전체|전지역|모두)%?['\"]", re.IGNORECASE),
        re.compile(r"festival_(loc|name)\s*=\s*['\"](전국|전체|전지역|모두)['\"]", re.IGNORECASE),
    ]
    if any(p.search(sql) for p in forbidden_patterns):
        return f"SELECT * FROM festival_info WHERE fin_date >= '{today}' ORDER BY start_date LIMIT 5"

    # 컬럼 체크
    known_columns = {"festival_name", "festival_loc", "start_date", "fin_date", "distance"}
    used_columns = set(re.findall(r"festival_\w+", sql))
    if used_columns - known_columns:
        return f"SELECT * FROM festival_info WHERE fin_date >= '{today}' ORDER BY start_date LIMIT 5"

    # LIMIT 5 삽입
    if "limit" not in sql.lower():
        sql += " LIMIT 5"

    return sql.strip()

def generate_recommendation_by_intent(intent: str, rows: List[dict], day: str) -> str:
    bullet = "\n".join(
        f"- {r.get('festival_name', '')} @ {r.get('festival_loc', '')} ({r.get('start_date')}~{r.get('fin_date')})"
        for r in rows)
    prompt = f"{day} 기준으로 추천할 축제를 자연스럽게 2~3문장으로 소개해 주세요:\n{bullet}"
    return generate_response(prompt)

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

def _check_file(p: pathlib.Path, hint: str = ""):
    if not p.exists():
        logger.error(f"파일 없음: {p}")
        if hint:
            logger.error(hint)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preprocess", action="store_true")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--test", type=str)
    parser.add_argument("--ask", type=str)
    args = parser.parse_args()

    if args.preprocess:
        preprocess_data()
    if args.train:
        train_intent_model()
    if args.test:
        print("[INTENT]", NLUEngine.classify_intent(args.test))
        print("[ENTITY]", [f"{e.type}:{e.value}" for e in NLUEngine.extract_entities(args.test)])
    if args.ask:
        print("[ASK]", args.ask)
        print("[BOT]", NLUEngine.answer(args.ask))

if __name__ == "__main__":
    main()