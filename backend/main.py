# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze

app = FastAPI(title="기업 평판 분석 API")

# React(localhost:5173)에서 오는 요청 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "기업 평판 분석 API 서버 실행 중"}