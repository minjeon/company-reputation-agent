# backend/routers/analyze.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pydantic import BaseModel
from src.orchestrator import run as orchestrator_run

router = APIRouter()


class AnalyzeRequest(BaseModel):
    company_name: str


class AnalyzeResponse(BaseModel):
    company_name: str
    analysis: dict
    agent_logs: list


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_company(request: AnalyzeRequest):
    """회사명을 받아서 평판 분석 결과 반환"""
    company_name = request.company_name.strip()

    analysis, agent_logs = orchestrator_run(company_name, verbose=False)

    return AnalyzeResponse(
        company_name=company_name,
        analysis=analysis,
        agent_logs=agent_logs
    )

@router.get("/report/{company_name}")
async def download_report(company_name: str):
    """저장된 리포트 파일 다운로드"""
    outputs_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "outputs"
    )

    files = [
        f for f in os.listdir(outputs_dir)
        if f.startswith(company_name) and f.endswith(".txt")
    ]

    if not files:
        raise HTTPException(status_code=404, detail="리포트 파일이 없습니다.")

    latest = sorted(files)[-1]
    file_path = os.path.join(outputs_dir, latest)

    return FileResponse(
        path=file_path,
        filename=latest,
        media_type="text/plain; charset=utf-8"
    )