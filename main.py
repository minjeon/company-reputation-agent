# 사용자가 직접 실행하는 진입점 파일 -> 회사명을 받아서 오케스트레이터에 넘기는 역할 

from src.orchestrator import run


def main():
    print("=" * 60)
    print("       기업 평판 분석 에이전트")
    print("=" * 60)

    # 회사명 입력
    company_name = input("\n분석할 회사명을 입력하세요: ").strip()

    if not company_name:
        print("❌ 회사명을 입력해주세요.")
        return

    # 오케스트레이터 실행
    analysis, agent_logs = run(company_name)


if __name__ == "__main__":
    main()