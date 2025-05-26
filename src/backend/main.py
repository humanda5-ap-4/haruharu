from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import re
import json
import torch
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForCausalLM
import engine
# FastAPI 초기화
app = FastAPI()
import uvicorn


import os

# CORS 허용 (필요 시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 및 컴포넌트 지연 로딩을 위한 변수
vec, clf, matcher, kogpt_tok, kogpt_model, device = [None] * 6

# 모델 로딩 함수
def load_models():
    global vec, clf, matcher, kogpt_tok, kogpt_model, device
    if vec is None or clf is None:
        print("[Load] Loading intent model and vectorizer...")
        vec = joblib.load("nlu/intent_vec.joblib")
        clf = joblib.load("nlu/intent_clf.joblib")
        with open("data/splits/entity_regex.json", encoding="utf-8") as f:
            patterns_dict = json.load(f)
        matcher = {k: re.compile(p) for k, p in patterns_dict.items()}
        print("[Load] Loading KoGPT tokenizer & model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        MODEL_NAME = "skt/kogpt2-base-v2"
        kogpt_tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        kogpt_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
        print("[Load] Done.")

# 슬랭 정규화
with open("data/slang.json", encoding="utf-8") as f:
    slang = json.load(f)

def normalize(txt: str) -> str:
    for k, v in slang.items():
        txt = re.sub(fr"\b{k}\b", v, txt)
    return txt

# 개체명 추출
def extract_entities(text: str):
    ents = []
    seen = set()
    for label, rx in matcher.items():
        for m in rx.finditer(text):
            val = m.group()
            key = (label, val, m.start(), m.end())
            if key not in seen:
                ents.append({
                    "type": label,
                    "value": val,
                    "start": m.start(),
                    "end": m.end(),
                })
                seen.add(key)
    return ents



# KoGPT 응답 생성
class Engine:
    def kogpt_answer(self, txt, intent, ents):
        ent_str = ", ".join(f"{e['type']}:{e['value']}" for e in ents)
        prompt = (
            f"[사용자]: {txt}\n"
            f"[의도]: {intent}\n"
            f"[개체]: {ent_str}\n"
            f"[챗봇]:"
        )
        inputs = self.kogpt_tok(prompt, return_tensors="pt").to(self.device)
        gen = kogpt_model.generate(
        **inputs,
        max_new_tokens=64,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
        eos_token_id=kogpt_tok.eos_token_id,  # 종료 토큰 지정
        pad_token_id=kogpt_tok.pad_token_id,  # 패딩 토큰 지정
        no_repeat_ngram_size=2,                # 2-gram 이상 반복 방지
    )

        return self.kogpt_tok.decode(gen[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)


# 기본 라우트
@app.get("/")
def root():
    return {"message": "Hello from NLP engine!"}

# 챗봇 API 엔드포인트
@app.post("/api/chat")
async def chat(msg: str = Body(..., embed=True)):
    if not msg.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어 있습니다.")
    engine.load_models()
    txt = engine.normalize(msg)
    intent = engine.clf.predict(engine.vec.transform([txt]))[0]
    ents = engine.matcher.extract(txt)
    answer = engine.kogpt_answer(txt, intent, ents)
    return {"intent": intent, "entities": ents, "answer": answer}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
