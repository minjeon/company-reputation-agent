import os
from datetime import datetime
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

CURRENT_YEAR = datetime.now().year
YEAR_RANGE = f"{CURRENT_YEAR - 2} {CURRENT_YEAR - 1} {CURRENT_YEAR}"


def search_company_news(company_name: str) -> list[dict]:
    """최신 뉴스 검색 — 긍정/부정 균형있게"""
    results = []

    try:
        pos = client.search(
            query=f"{company_name} 기업 성과 실적 {YEAR_RANGE}",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in pos.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 뉴스 긍정 검색 실패: {e}")

    try:
        neg = client.search(
            query=f"{company_name} 논란 리스크 문제 {YEAR_RANGE}",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in neg.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 뉴스 부정 검색 실패: {e}")

    return results


def search_company_culture(company_name: str) -> list[dict]:
    """기업 문화/복지/워라밸 검색 — 긍정/부정 균형있게"""
    results = []

    try:
        pos = client.search(
            query=f"{company_name} 복지 연봉 워라밸 장점",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in pos.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 기업문화 긍정 검색 실패: {e}")

    try:
        neg = client.search(
            query=f"{company_name} 복지 연봉 워라밸 단점 불만",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in neg.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 기업문화 부정 검색 실패: {e}")

    return results


def search_company_review(company_name: str) -> list[dict]:
    """잡플래닛 등 리뷰 사이트 검색 — 긍정/부정 균형있게"""
    results = []

    try:
        pos = client.search(
            query=f"{company_name} 잡플래닛 블라인드 장점 추천",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in pos.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 리뷰 긍정 검색 실패: {e}")

    try:
        neg = client.search(
            query=f"{company_name} 잡플래닛 블라인드 단점 퇴사",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in neg.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 리뷰 부정 검색 실패: {e}")

    return results


def search_company_growth(company_name: str) -> list[dict]:
    """성장성/재무/사업 방향 검색 — 긍정/부정 균형있게"""
    results = []

    try:
        pos = client.search(
            query=f"{company_name} 실적 성장 매출 전망 {YEAR_RANGE}",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in pos.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 성장성 긍정 검색 실패: {e}")

    try:
        neg = client.search(
            query=f"{company_name} 실적 부진 위기 리스크 {YEAR_RANGE}",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in neg.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 성장성 부정 검색 실패: {e}")

    return results


def search_company_leadership(company_name: str) -> list[dict]:
    """경영진/리더십 전용 검색 — 긍정/부정 균형있게"""
    results = []

    try:
        pos = client.search(
            query=f"{company_name} 대표 경영진 리더십 비전 성과",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in pos.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 리더십 긍정 검색 실패: {e}")

    try:
        neg = client.search(
            query=f"{company_name} 대표 경영진 논란 비판 리더십 문제",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in neg.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 리더십 부정 검색 실패: {e}")

    return results


def search_company_image(company_name: str) -> list[dict]:
    """대외이미지 전용 검색 — 긍정/부정 균형있게"""
    results = []

    try:
        pos = client.search(
            query=f"{company_name} 브랜드 이미지 평판 사회공헌 ESG",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in pos.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 대외이미지 긍정 검색 실패: {e}")

    try:
        neg = client.search(
            query=f"{company_name} 논란 규제 사건 사고 비판 {YEAR_RANGE}",
            search_depth="advanced",
            max_results=5,
        )
        results += [
            r for r in neg.get("results", [])
            if any(ord(c) > 0xAC00 for c in r.get("content", "")[:200])
        ]
    except Exception as e:
        print(f"⚠️ 대외이미지 부정 검색 실패: {e}")

    return results


def run_all_searches(company_name: str) -> dict:
    """6개 검색을 한 번에 실행"""
    return {
        "search_company_news":       search_company_news(company_name),
        "search_company_culture":    search_company_culture(company_name),
        "search_company_review":     search_company_review(company_name),
        "search_company_growth":     search_company_growth(company_name),
        "search_company_leadership": search_company_leadership(company_name),
        "search_company_image":      search_company_image(company_name),
    }