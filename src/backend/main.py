# sql

import random
from fastapi import Depends
from sqlalchemy.orm import Session
import DB.crud
from DB.services import intent_handlers

from DB.db import get_db


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

# src/backend/main.py
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import engine

app = FastAPI()
import uvicorn


import os

# CORS 허용 (필요 시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174"],  # 실제 배포시에는 특정 origin으로 제한
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
def kogpt_answer(txt, intent, ents):
    ent_str = ", ".join(f"{e['type']}:{e['value']}" for e in ents)
    prompt = (
        f"사용자: {txt}\n"
        f"의도: {intent}\n"
        f"개체: {ent_str}\n"
        f"답변: "
    )

    inputs = kogpt_tok(prompt, return_tensors="pt").to(device)
    gen = kogpt_model.generate(
        **inputs,
        max_new_tokens=64,
        do_sample=True,
        top_p=0.9,
        temperature=0.7,
        eos_token_id=kogpt_tok.eos_token_id or kogpt_tok.pad_token_id,
        pad_token_id=kogpt_tok.pad_token_id,
        no_repeat_ngram_size=3,
        repetition_penalty=1.2,
    )

    result = kogpt_tok.decode(
        gen[0, inputs.input_ids.shape[1]:],
        skip_special_tokens=True
    ).strip()
    
    return result

# 기본 라우트
@app.get("/")
def root():
    return {"message": "Hello from NLP engine!"}

# 챗봇 API 엔드포인트
#@app.post("/api/chat")
#async def chat(msg: str = Body(..., embed=True)):
#    if not msg.strip():
#        raise HTTPException(status_code=400, detail="메시지가 비어 있습니다.")
#    engine.load_models()
#    txt = engine.normalize(msg)
#    intent = engine.clf.predict(engine.vec.transform([txt]))[0]
#    ents = engine.matcher.extract(txt)
#    answer = engine.kogpt_answer(txt, intent, ents)
#    return {"intent": intent, "entities": ents, "answer": answer}


#@app.post("/api/chat")
#async def chat(msg: str = Body(..., embed=True)):
#    if not msg.strip():
#       raise HTTPException(status_code=400, detail="메시지가 비어 있습니다.")
#    engine.load_models()
#    
#    txt = engine.normalize(msg)
#    intent = engine.clf.predict(engine.vec.transform([txt]))[0]
#    ents = engine.matcher.extract(txt) 
#    print(f"사용자 입력: {msg}")
#    print(f"정규화된 입력: {txt}")
#    print(f"의도 분류 결과: {intent}")
#    print(f"추출된 개체: {ents}")
#
#    answer = engine.kogpt_answer(txt, intent, ents)
#    return {"intent": intent, "entities": ents, "answer": answer}
default_responses = [
    "아직 그 주제에 대해선 공부 중이에요. 조금만 기다려 주세요!",
    "아쉽게도 지금은 답변을 준비하고 있어요. 곧 더 좋은 답변 드릴게요.",
    "해당 내용에 대해선 더 알아보고 알려드릴게요!",
    "그 부분에 대해선 지금 바로 답변을 드리기 어려워서 죄송해요.",
    "조금만 기다려 주세요, 곧 더 정확한 정보를 드릴 수 있도록 할게요."
]

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
@app.on_event("startup")
def startup_event():
    print("[INFO] FastAPI 서버가 시작되었습니다.")
    engine.load_models()
    print(f"[INFO] main sees clf: {engine.clf}, vec: {engine.vec}")

@app.post("/chat")
async def chat(
    msg: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    if not msg.strip():
        return {"error": "메시지가 비어 있습니다."}

    engine.load_models()

    txt = engine.normalize(msg)
    intent = engine.clf.predict(engine.vec.transform([txt]))[0]
    ents = engine.matcher.extract(txt)

    print(f"사용자 입력: {msg}")
    print(f"정규화된 입력: {txt}")
    print(f"의도 분류 결과: {intent}")
    print(f"추출된 개체: {ents}")

    handler = intent_handlers.get(intent)
    if handler:
        answer = handler(db, ents)
    else:
        answer = random.choice(default_responses)

    return {"intent": intent, "entities": ents, "answer": answer}


# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json()
#     msg = data.get("msg")
#     # 실제 챗봇 답변 생성 로직으로 교체
#     # 예시: 기존 search 함수 파이프라인 활용
#     text = normalize(msg)
#     intent = clf.predict(vec.transform([text]))[0]
#     ents = matcher.extract(text)
#     from engine import kogpt_tok, kogpt_model, device
#     answer = kogpt_answer(text, intent, ents, kogpt_tok, kogpt_model, device)
#     return {"answer": answer}

# -- 확인용 코드 -- 
# @app.get("/api/search")
# def search(category: str = Query(...), query: str = Query(...)):
#     text = normalize(query)
#     intent = clf.predict(vec.transform([text]))[0]
#     ents = matcher.extract(text)
#     from engine import kogpt_tok, kogpt_model, device
#     answer = kogpt_answer(text, intent, ents, kogpt_tok, kogpt_model, device)
#     return {"result": answer}
