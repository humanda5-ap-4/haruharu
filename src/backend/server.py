# server.py
""" execute 
uvicorn server:app --reload
python server.py
"""
import os
from fastapi import FastAPI, Body, HTTPException
import uvicorn
import engine  # 위에서 작성한 engine.py

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NLP Chatbot API",
    version="1.0.0",
    description="의도 분류 + KoGPT 기반 챗봇 서비스"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 개발 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/chat")
async def chat(msg: str = Body(..., embed=True)):
    if not msg.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어 있습니다.")
    engine.load_models()
    txt = engine.normalize(msg)
    intent = engine.clf.predict(engine.vec.transform([txt]))[0]
    ents = engine.matcher.extract(txt)
    answer = engine.kogpt_answer(txt, intent, ents,
                                 engine.kogpt_tok, engine.kogpt_model, engine.device)
    return {"intent": intent, "entities": ents, "answer": answer}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
