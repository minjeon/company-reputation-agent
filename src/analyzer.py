# web_search.py가 수집한 텍스트를 받아서 OpenAI API로 분류하고 점수 매기는 파일

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 분류할 카테고리 정의
CATEGORIES = {
    "복지/연봉":   "급여 수준, 복리후생, 인센티브 관련 내용",
    "워라밸":     "업무 강도, 야근, 휴가 사용 자유도 관련 내용",
    "기업문화":   "조직 분위기, 수평/수직 문화, 내부 소통 관련 내용",
    "성장가능성": "회사 실적, 사업 확장, 미래 전망 관련 내용",
    "대외이미지": "언론 보도, 사회적 평판, 브랜드 이미지 관련 내용",
    "리더십":     "경영진 신뢰도, 의사결정 방식 관련 내용",
}

# 카테고리별 관련 소스 매핑
CATEGORY_SOURCE_MAP = {
    "복지/연봉":   ["search_company_culture", "search_company_review"],
    "워라밸":     ["search_company_culture", "search_company_review"],
    "기업문화":   ["search_company_culture", "search_company_review"],
    "성장가능성": ["search_company_growth"],
    "대외이미지": ["search_company_image",      "search_company_news"],
    "리더십":     ["search_company_leadership", "search_company_news"],
}


# ─────────────────────────────────────────
# 점수 계산 공식
# ─────────────────────────────────────────
def _calculate_score(positive: int, negative: int):
    """긍정/부정 개수로 점수를 코드로 직접 계산"""
    total = positive + negative

    # 근거 2개 미만이면 신뢰 불가 → null
    if total < 2:
        return None

    ratio = positive / total

    if ratio >= 0.95:
        return 10
    elif ratio >= 0.85:
        return 9
    elif ratio >= 0.75:
        return 8
    elif ratio >= 0.65:
        return 7
    elif ratio >= 0.55:
        return 6
    elif ratio >= 0.45:
        return 5
    elif ratio >= 0.35:
        return 4
    elif ratio >= 0.25:
        return 3
    elif ratio >= 0.15:
        return 2
    else:
        return 1


# ─────────────────────────────────────────
# 카테고리별 관련 텍스트 추출
# ─────────────────────────────────────────
def _extract_texts_for_category(
    category: str,
    search_results: dict
) -> list[str]:
    """카테고리에 매핑된 소스에서만 텍스트 추출"""
    sources = CATEGORY_SOURCE_MAP.get(category, list(search_results.keys()))
    texts = []
    for source in sources:
        for item in search_results.get(source, []):
            content = item.get("content", "")
            if content:
                texts.append(content)
    return texts[:20]  # 카테고리당 최대 20개


# ─────────────────────────────────────────
# 프롬프트 생성
# ─────────────────────────────────────────
def _build_prompt(company_name: str, category: str, description: str, texts: list[str]) -> str:
    """카테고리별 단일 프롬프트 생성"""
    joined_texts = "\n\n".join(texts)

    return f"""
다음은 '{company_name}'에 대해 수집된 텍스트입니다.

[분석할 카테고리]
{category}: {description}

[수집된 텍스트]
{joined_texts}

[역할]
위 텍스트에서 '{category}' 카테고리에 해당하는 내용을 찾아서 긍정/부정으로 분류하고 개수를 세세요.

[긍정/부정 판단 기준]
긍정: 해당 카테고리에 대해 좋은 평가, 만족, 성과, 개선을 나타내는 내용
부정: 해당 카테고리에 대해 나쁜 평가, 불만, 문제, 논란을 나타내는 내용
중립: 단순 사실 전달 (카운트 제외)

[중요 규칙]
1. 수집된 텍스트에 명확한 근거가 있는 경우에만 카운트하세요
2. 추측하거나 상식으로 채우지 마세요
3. 카테고리와 무관한 텍스트는 무시하세요
4. evidence는 반드시 수집된 텍스트에서 그대로 가져오세요 (재작성 금지)
5. 관련 텍스트가 없으면 positive_count=0, negative_count=0으로 반환하세요

아래 JSON 형식으로만 응답하세요:
{{
    "positive_count": 긍정 텍스트 개수(정수),
    "negative_count": 부정 텍스트 개수(정수),
    "summary": "2~3문장 요약",
    "evidence": ["근거 텍스트 1", "근거 텍스트 2", "근거 텍스트 3"]
}}
"""


# ─────────────────────────────────────────
# 카테고리별 단일 분석
# ─────────────────────────────────────────
def _analyze_category(
    company_name: str,
    category: str,
    description: str,
    texts: list[str]
) -> dict:
    """카테고리 하나를 분석"""
    try:
        if not texts:
            return {
                "positive_count": 0,
                "negative_count": 0,
                "score": None,
                "score_basis": "수집된 텍스트 없음",
                "summary": "관련 정보를 수집하지 못했습니다.",
                "evidence": []
            }

        prompt = _build_prompt(company_name, category, description, texts)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 텍스트 분류 전문가입니다. 반드시 JSON 형식으로만 응답하세요. 점수는 절대 계산하지 마세요."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # 점수 코드로 직접 계산
        pos = data.get("positive_count", 0)
        neg = data.get("negative_count", 0)
        score = _calculate_score(pos, neg)

        data["score"] = score
        data["score_basis"] = (
            f"긍정 {pos}개, 부정 {neg}개 → {score}점"
            if score is not None
            else "근거 부족 (관련 텍스트 2개 미만)"
        )

        return data

    except json.JSONDecodeError as e:
        print(f"⚠️ [{category}] JSON 파싱 실패: {e}")
        return {"score": None, "score_basis": "파싱 실패", "summary": "", "evidence": []}
    except Exception as e:
        print(f"⚠️ [{category}] 분석 실패: {e}")
        return {"score": None, "score_basis": "분석 오류", "summary": "", "evidence": []}


# ─────────────────────────────────────────
# 메인 분석 함수
# ─────────────────────────────────────────
def analyze(company_name: str, search_results: dict) -> dict:
    """카테고리별로 분리해서 분석"""
    result = {}

    for category, description in CATEGORIES.items():
        print(f"  📊 [{category}] 분석 중...")

        # 카테고리에 맞는 소스에서만 텍스트 추출
        texts = _extract_texts_for_category(category, search_results)

        # 카테고리별 분석
        result[category] = _analyze_category(
            company_name, category, description, texts
        )

    return result


# ─────────────────────────────────────────
# 근거 검증
# ─────────────────────────────────────────
def verify_evidence(analysis: dict, search_results: dict) -> dict:
    """근거 텍스트가 실제 수집 원문에 존재하는지 확인"""
    try:
        all_texts = " ".join([
            item.get("content", "")
            for results in search_results.values()
            for item in results
        ])

        verified = {}
        for category, data in analysis.items():
            if not isinstance(data, dict):
                continue

            evidence_list = data.get("evidence", [])
            verified_evidence = []

            for ev in evidence_list:
                keywords = ev[:15]
                is_found = keywords in all_texts
                verified_evidence.append({
                    "text": ev,
                    "verified": is_found
                })

            verified[category] = {
                **data,
                "evidence": verified_evidence
            }

        return verified

    except Exception as e:
        print(f"⚠️ 근거 검증 실패: {e}")
        return analysis