# src/backend/main.py
# 에러제거용 ----  
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#--------
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mock_engine import search_by_category_and_name
import os

app = FastAPI()



frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")

app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 origin으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
def search(category: str = Query(...), query: str = Query(...)):
    result = search_by_category_and_name(category, query)
    return result
