import os
import json
import re
import pathlib
import random
import pandas as pd
import numpy as np
import joblib
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from fastapi import FastAPI, Body
from transformers import AutoTokenizer, AutoModelForCausalLM
import uvicorn

# -- 전처리 함수 정의 ------------------------------------------------
def preprocess_data():
    # Intent 데이터 로드·셔플·split(8:1:1)
    print("[Preprocess] Splitting intent dataset...")
    ints = pd.read_json("data/intent_dataset.json", encoding="utf-8")
    ints = ints.sample(frac=1, random_state=42)
    train, valid, test = np.split(ints, [int(.8*len(ints)), int(.9*len(ints))])
    splits_dir = pathlib.Path("data/splits")
    splits_dir.mkdir(parents=True, exist_ok=True)
    train.to_json(splits_dir / "intent_train.json", orient="records", force_ascii=False)

    # Entity 정규식 생성
    print("[Preprocess] Building entity regex patterns...")
    gaz = json.load(open("data/entity_dataset.json", encoding="utf-8"))
    patterns = {k: re.compile("|".join(map(re.escape, v))) for k, v in gaz.items()}
    with open(splits_dir / "entity_regex.json", "w", encoding="utf-8") as f:
        json.dump({k: v.pattern for k, v in patterns.items()}, f, ensure_ascii=False, indent=2)

    # Slang normalization은 로딩만 해두면 됨
    print("[Preprocess] Done.")

# -- Intent 모델 학습 함수 정의 ----------------------------------------
def train_intent_model():
    print("[Train] Training intent classification model...")
    pathlib.Path("nlu").mkdir(exist_ok=True)
    train = pd.read_json("data/splits/intent_train.json", encoding="utf-8")
    vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", ngram_range=(1,2))
    clf = LinearSVC().fit(vec.fit_transform(train.text), train.intent)
    joblib.dump(vec, "nlu/intent_vec.joblib")
    joblib.dump(clf, "nlu/intent_clf.joblib")
    print("[Train] Done.")

# -- Entity 추출기 클래스 정의 -----------------------------------------
class EntityMatcher:
    def __init__(self, pattern_path: str = "data/splits/entity_regex.json"):
        patterns_dict = json.load(open(pattern_path, encoding="utf-8"))
        self.patterns = {k: re.compile(p) for k, p in patterns_dict.items()}
    def extract(self, text: str):
        ents = []
        for label, rx in self.patterns.items():
            for m in rx.finditer(text):
                ents.append({
                    "type": label,
                    "value": m.group(),
                    "start": m.start(),
                    "end": m.end(),
                })
        return ents

# -- Slang-normalize 함수 정의 -----------------------------------------
slang = json.load(open("data/slang.json", encoding="utf-8"))

def normalize(txt: str) -> str:
    for k, v in slang.items():
        txt = re.sub(fr"\b{k}\b", v, txt)
    return txt

# -- KoGPT 답변 생성 함수 정의 ----------------------------------------
def kogpt_answer(user: str, intent: str, ents: list, tok, model, device: str) -> str:
    ent_str = ", ".join(f"{e['type']}:{e['value']}" for e in ents)
    prompt = (
        f"[사용자]: {user}\n"
        f"[의도]: {intent}\n"
        f"[개체]: {ent_str}\n"
        f"[챗봇]:"
    )
    inputs = tok(prompt, return_tensors="pt").to(device)
    gen = model.generate(
        **inputs,
        max_new_tokens=64,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
    )
    return tok.decode(gen[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)

# -- 모델 로딩 (지연 로딩) ----------------------------------------------
vec, clf, matcher, kogpt_tok, kogpt_model, device = [None]*6

def load_models():
    global vec, clf, matcher, kogpt_tok, kogpt_model, device
    if vec is None or clf is None:
        print("[Load] Loading intent model and vectorizer...")
        vec = joblib.load("nlu/intent_vec.joblib")
        clf = joblib.load("nlu/intent_clf.joblib")
        matcher = EntityMatcher()
        print("[Load] Loading KoGPT tokenizer & model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        MODEL_NAME = "skt/kogpt2-base-v2"
        kogpt_tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        kogpt_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
        print("[Load] Done.")

# -- FastAPI 앱 및 엔드포인트 정의 -------------------------------------
app = FastAPI()

@app.post("/chat")
def chat(msg: str = Body(..., embed=True)):
    load_models()
    txt = normalize(msg)
    intent = clf.predict(vec.transform([txt]))[0]
    ents = matcher.extract(txt)
    answer = kogpt_answer(txt, intent, ents, kogpt_tok, kogpt_model, device)
    return {"intent": intent, "entities": ents, "answer": answer}

# -- 스크립트 실행 -----------------------------------------------------
if __name__ == "__main__":
    ans = input("모델훈련후 실행하겠습니까? (y/n): ").strip().lower()
    if ans == 'y':
        preprocess_data()
        train_intent_model()
    print("[Start] Running FastAPI server at http://127.0.0.1:8000")
    uvicorn.run("nlp_engine_execute:app", host="127.0.0.1", port=8000, reload=True)
