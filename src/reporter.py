# analyzer.py가 만든 카테고리별 점수와 근거를 받아서 읽기 좋은 리포트로 출력하고 파일로 저장하는 파일

import os
from datetime import datetime


def _get_score_bar(score) -> str:
    """점수를 시각적 바로 표현 (예: ████░░░░░░ 4/10)"""
    if score is None:
        return "정보 없음"
    filled = int(score)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"{bar} {score}/10"

def _get_confidence(evidence: list) -> str:
    """근거 수에 따른 신뢰도"""
    count = len(evidence)
    if count >= 3:
        return "🟢 높음"
    elif count >= 1:
        return "🟡 보통"
    else:
        return "🔴 낮음 (근거 부족)"

def _get_score_label(score) -> str:
    """점수 구간별 라벨"""
    if score is None:
        return "정보 없음"
    if score >= 8:
        return "✅ 우수"
    elif score >= 6:
        return "🔵 양호"
    elif score >= 4:
        return "🟡 보통"
    else:
        return "🔴 미흡"


def generate_report(company_name: str, analysis: dict) -> str:
    """분석 결과(딕셔너리)를 리포트 텍스트로 변환"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("=" * 60)
    lines.append(f"  {company_name} 기업 평판 분석 리포트")
    lines.append(f"  분석 일시: {now}")
    lines.append("=" * 60)

    # 에러 처리
    if "error" in analysis:
        lines.append(f"\n❌ 분석 실패: {analysis['error']}")
        return "\n".join(lines)

    # 전체 평균 점수 계산
    scores = [
        v["score"] for v in analysis.values()
        if isinstance(v, dict) and v.get("score") is not None
    ]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    lines.append(f"\n📊 종합 점수: {_get_score_bar(avg_score)}")
    lines.append(f"   평가: {_get_score_label(avg_score)}")
    lines.append("\n" + "-" * 60)

    # 카테고리별 상세 내용
    lines.append("\n📋 카테고리별 상세 분석\n")

    for category, data in analysis.items():
        if not isinstance(data, dict):
            continue

        score = data.get("score")
        summary = data.get("summary", "")
        evidence = data.get("evidence", [])
        score_basis = data.get("score_basis", "")
        positive_count = data.get("positive_count", 0) 
        negative_count = data.get("negative_count", 0)

        lines.append(f"▶ {category}")
        lines.append(f"  점수: {_get_score_bar(score)}  {_get_score_label(score)}")
        lines.append(f"  긍정: {positive_count}개 / 부정: {negative_count}개")  # ✅ 추가
        lines.append(f"  요약: {summary}")

        if evidence:
            lines.append(f"  신뢰도: {_get_confidence(evidence)}")
            lines.append("  근거:")
            for e in evidence:
                lines.append(f"    - {e}")

        if score_basis:
            lines.append(f"  채점 근거: {score_basis}")

        lines.append("")

    # 점수 높은 순 강점/약점 요약
    scored = {
        k: v["score"] for k, v in analysis.items()
        if isinstance(v, dict) and v.get("score") is not None
    }
    if scored:
        sorted_scores = sorted(scored.items(), key=lambda x: x[1], reverse=True)

        lines.append("-" * 60)
        lines.append("\n💪 강점 TOP 2")
        for category, score in sorted_scores[:2]:
            lines.append(f"  • {category}: {score}/10")

        lines.append("\n⚠️  개선 필요 TOP 2")
        for category, score in sorted_scores[-2:]:
            lines.append(f"  • {category}: {score}/10")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def save_report(company_name: str, report_text: str) -> str:
    """리포트를 outputs 폴더에 txt 파일로 저장"""
    os.makedirs("outputs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/{company_name}_reputation_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)
    return filename


def run_report(company_name: str, analysis: dict) -> None:
    """리포트 생성 + 출력 + 저장을 한 번에"""
    report_text = generate_report(company_name, analysis)

    # 터미널 출력
    print(report_text)

    # 파일 저장
    saved_path = save_report(company_name, report_text)
    print(f"\n💾 리포트 저장 완료: {saved_path}")

