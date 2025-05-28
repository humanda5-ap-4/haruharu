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

@app.on_event("startup")
def startup_event():
    print("[INFO] FastAPI 서버가 시작되었습니다.")
    engine.load_models()
    print(f"[INFO] main sees clf: {engine.clf}, vec: {engine.vec}")

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        msg = data.get("msg")
        text = engine.normalize(msg)
        
        # clf/vec None 체크
        if engine.clf is None or engine.vec is None:
            raise HTTPException(status_code=500, detail="Classifier not loaded")
            
        intent = engine.clf.predict(engine.vec.transform([text]))[0]
        ents = engine.matcher.extract(text)
        
        answer = engine.kogpt_answer(text, intent, ents, engine.kogpt_tok, engine.kogpt_model, engine.device)
        return {"answer": answer}
    except Exception as e:
        print("Error in /chat:", str(e))  # 터미널에 에러 출력
        raise HTTPException(status_code=500, detail=str(e))
    

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
