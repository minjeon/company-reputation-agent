import json
import os
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv

from src.tools.web_search import (
    search_company_news,
    search_company_culture,
    search_company_review,
    search_company_growth,
    search_company_leadership,  
    search_company_image,       
)
from src.analyzer import analyze, verify_evidence
from src.reporter import run_report

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────────────────
# LLM에게 알려줄 도구 목록 정의
# ─────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_company_news",
            "description": "회사의 최신 뉴스, 성과, 논란, 이슈를 검색한다. 대외이미지나 리더십 관련 정보가 필요할 때 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "검색할 회사명"}
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_culture",
            "description": "회사의 기업문화, 복지, 워라밸, 직원 후기를 검색한다. 복지/연봉, 워라밸, 기업문화 정보가 필요할 때 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "검색할 회사명"}
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_review",
            "description": "잡플래닛, 블라인드 등 리뷰 사이트에서 직원 리뷰를 검색한다. 전반적인 직원 만족도 파악에 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "검색할 회사명"}
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_growth",
            "description": "회사의 실적, 성장성, 미래 전망, 사업 방향을 검색한다. 성장가능성 정보가 필요할 때 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "검색할 회사명"}
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_leadership",
            "description": "회사 대표, 경영진, CEO의 리더십과 의사결정 방식을 검색한다. 리더십 카테고리 정보가 필요할 때 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "검색할 회사명"}
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_image",
            "description": "회사의 브랜드 이미지, 평판, 사회공헌, ESG를 검색한다. 대외이미지 카테고리 정보가 필요할 때 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "검색할 회사명"}
                },
                "required": ["company_name"]
            }
        }
    },
]

# 도구 이름 → 실제 함수 매핑
TOOL_FUNCTIONS = {
    "search_company_news":    search_company_news,
    "search_company_culture": search_company_culture,
    "search_company_review":  search_company_review,
    "search_company_growth":  search_company_growth,
    "search_company_leadership": search_company_leadership,  
    "search_company_image":      search_company_image,
}


# ─────────────────────────────────────────
# 도구 실행
# ─────────────────────────────────────────
def _execute_tool(tool_name: str, company_name: str) -> list:
    """LLM이 선택한 도구 실행"""
    try:
        func = TOOL_FUNCTIONS.get(tool_name)
        if func is None:
            print(f"⚠️ 알 수 없는 도구: {tool_name}")
            return []
        return func(company_name)
    except Exception as e:
        print(f"⚠️ 도구 실행 실패 ({tool_name}): {e}")
        return []


def _execute_tools_parallel(tool_calls: list, company_name: str) -> list:
    """LLM이 여러 도구를 동시에 요청하면 병렬 실행"""
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_execute_tool, tc.function.name, company_name): tc
            for tc in tool_calls
        }
        for future, tc in futures.items():
            result = future.result()
            results.append({
                "tool_call_id": tc.id,
                "name": tc.function.name,
                "result": result
            })

    return results


# ─────────────────────────────────────────
# 에이전틱 루프
# ─────────────────────────────────────────



def _agentic_loop(company_name: str, verbose: bool = True) -> dict:
    """
    LLM이 스스로 도구를 선택하고 충분한 정보가 모이면 멈추는 루프
    """
    agent_logs = []

    messages = [
        {
            "role": "system",
            "content": """당신은 기업 평판 분석 전문가입니다.
                    주어진 도구들을 사용해서 회사에 대한 충분한 정보를 수집하세요.

수집 전략:
1. 필요한 도구를 판단해서 호출하세요 (여러 개 동시 호출 가능)
2. 결과를 보고 정보가 부족한 카테고리가 있으면 추가 검색하세요
3. 6개 카테고리(복지/연봉, 워라밸, 기업문화, 성장가능성, 대외이미지, 리더십)에 대해
   충분한 정보가 모이면 DONE이라고 말하고 멈추세요
4. 최대 3라운드 이내에 완료하세요

[도구-카테고리 매핑]
- 복지/연봉, 워라밸, 기업문화 → search_company_culture, search_company_review
- 성장가능성                   → search_company_growth
- 대외이미지                   → search_company_image, search_company_news
- 리더십                       → search_company_leadership, search_company_news"""
        },
        {
            "role": "user",
            "content": f"'{company_name}' 회사의 평판을 분석하기 위한 정보를 수집해주세요."
        }
    ]

    all_search_results = {}  # 수집된 전체 결과 누적
    round_count = 0
    max_rounds = 3

    while round_count < max_rounds:
        round_count += 1
        if verbose:
            print(f"\n🔄 Round {round_count}")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            print(f"⚠️ LLM 호출 실패 (Round {round_count}): {e}")
            break

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            if verbose:
                print(f"✅ LLM 판단: 수집 완료 ({msg.content})")
            break

        if verbose:
            tool_names = [tc.function.name for tc in msg.tool_calls]
            print(f"🛠️  선택한 도구: {tool_names} (병렬 실행)")

        tool_results = _execute_tools_parallel(msg.tool_calls, company_name)
        agent_logs.append(f"Round {round_count}: {[tc.function.name for tc in msg.tool_calls]} 실행")

        for tr in tool_results:
            all_search_results[tr["name"]] = tr["result"]
            messages.append({
                "role": "tool",
                "tool_call_id": tr["tool_call_id"],
                "content": json.dumps(tr["result"], ensure_ascii=False)
            })

            if verbose:
                print(f"  ✅ {tr['name']}: {len(tr['result'])}개 문서 수집")

    # 아무것도 수집 못했을 때 방어
    if not all_search_results:
        print("⚠️ 수집된 정보가 없습니다. 기본 검색으로 대체합니다.")
        from src.tools.web_search import run_all_searches
        all_search_results = run_all_searches(company_name)

    return all_search_results, agent_logs


# ─────────────────────────────────────────
# 메인 실행 함수
# ─────────────────────────────────────────
def run(company_name: str, verbose: bool = True) -> dict:
    """오케스트레이터 메인 실행 함수"""
    try:
        print("=" * 60)
        print(f"  기업 평판 분석 시작: {company_name}")
        print("=" * 60)

        print(f"\n🤖 AI가 수집 전략 판단 중...")
        search_results, agent_logs = _agentic_loop(company_name, verbose=verbose)

        os.makedirs("outputs", exist_ok=True)
        with open(f"outputs/{company_name}_raw.json", "w", encoding="utf-8") as f:
            json.dump(search_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 원문 저장 완료: outputs/{company_name}_raw.json")

        print("\n🤖 AI 분석 중...")
        analysis = analyze(company_name, search_results)
        analysis = verify_evidence(analysis, search_results)
        print("✅ 분석 완료")

        print("\n📝 리포트 생성 중...")
        run_report(company_name, analysis)

        return analysis, agent_logs

    except Exception as e:
        print(f"❌ 전체 분석 실패: {e}")
        return {"error": str(e)}, []  # 튜플로 반환