import streamlit as st
import plotly.graph_objects as go
import os

from src.reporter import generate_report, save_report
from src.orchestrator import run as orchestrator_run

# ─────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="기업 평판 분석",
    page_icon="🏢",
    layout="centered"
)


# ─────────────────────────────────────────
# 레이더 차트
# ─────────────────────────────────────────
def draw_radar_chart(analysis: dict):
    categories = []
    scores = []

    for cat, data in analysis.items():
        if isinstance(data, dict) and data.get("score") is not None:
            categories.append(cat)
            scores.append(data["score"])

    if not categories:
        return None

    # 레이더 차트는 닫힌 도형이어야 해서 첫 값을 마지막에 추가
    categories_closed = categories + [categories[0]]
    scores_closed = scores + [scores[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(99, 179, 237, 0.3)",
        line=dict(color="rgba(99, 179, 237, 1)", width=2),
        name="점수"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
        ),
        showlegend=False,
        margin=dict(t=40, b=40),
        height=400,
    )
    return fig


# ─────────────────────────────────────────
# 점수 색상
# ─────────────────────────────────────────
def score_label(score):
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


# ─────────────────────────────────────────
# session_state 초기화
# ─────────────────────────────────────────
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "report_path" not in st.session_state:
    st.session_state.report_path = None
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []


# ─────────────────────────────────────────
# 메인 UI
# ─────────────────────────────────────────
st.title("🏢 기업 평판 분석 에이전트")
st.caption("회사명을 입력하면 웹/뉴스/리뷰를 수집해서 AI가 분석해드려요.")

st.divider()

# 입력창
company_name = st.text_input(
    "분석할 회사명을 입력하세요",
    placeholder="예: 카카오, 삼성전자, 네이버"
)
start_btn = st.button("🔍 분석 시작", use_container_width=True)

# ─────────────────────────────────────────
# 분석 실행
# ─────────────────────────────────────────
if start_btn:
    if not company_name.strip():
        st.warning("회사명을 입력해주세요.")
    else:
        with st.status(f"🤖 AI가 '{company_name}' 분석 전략 수립 중...", expanded=True) as status:
            st.write("AI가 필요한 정보를 판단하고 수집합니다...")
            analysis, agent_logs = orchestrator_run(company_name, verbose=False)
            st.session_state.analysis = analysis
            st.session_state.agent_logs = agent_logs
            st.session_state.company_name = company_name
            st.write("✅ 분석 완료")
            status.update(label="✅ 분석 완료!", state="complete")



# ─────────────────────────────────────────
# 결과 출력 — if start_btn 바깥에 있어야 함 ✅
# ─────────────────────────────────────────
if st.session_state.analysis is not None:
    analysis = st.session_state.analysis
    company_name = st.session_state.company_name

    if st.session_state.agent_logs:
        with st.expander("🤖 AI 수집 과정 보기"):
            for log in st.session_state.agent_logs:
                st.write(f"✅ {log}")

    st.divider()

    # ── 종합 점수 ──
    scores = [
        v["score"] for v in analysis.values()
        if isinstance(v, dict) and v.get("score") is not None
    ]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    st.subheader("📊 종합 점수")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="평균 점수", value=f"{avg_score} / 10" if avg_score else "N/A")
        st.markdown(f"**평가:** {score_label(avg_score)}")
    with col2:
        if avg_score:
        # 점수가 10 초과일 경우 대비해서 clamp 처리
            safe_score = min(max(avg_score / 10, 0.0), 1.0)
            st.progress(safe_score)

    st.divider()

    # ── 레이더 차트 ──
    st.subheader("📡 카테고리별 점수 분포")
    fig = draw_radar_chart(analysis)
    if fig:
        st.plotly_chart(fig, width='stretch')

    st.divider()

    # ── 카테고리별 상세 ──
    st.subheader("📋 카테고리별 상세 분석")

    for category, data in analysis.items():
        if not isinstance(data, dict):
            continue

        score = data.get("score")
        summary = data.get("summary", "")
        evidence = data.get("evidence", [])
        score_basis = data.get("score_basis", "")

        with st.expander(f"**{category}** — {score}/10  {score_label(score)}"):
            safe_score = min(max((score or 0) / 10, 0.0), 1.0)
            st.progress(safe_score)

            if score_basis:
                st.markdown(f"**채점 근거:** {score_basis}")

            if evidence:
                st.markdown("**근거 텍스트:**")
                for e in evidence:
                    if isinstance(e, dict):
                        verified = e.get("verified", False)
                        text = e.get("text", "")
                        verified_label = "👌 ( 출처확인 ) " if verified else "❓ ( 출처미확인 ) "
                        st.markdown(f"> {verified_label} {text}")
                    else:
                        st.markdown(f"> {e}")

    st.divider()

    # ── 강점 / 약점 ──
    scored = {
        k: v["score"] for k, v in analysis.items()
        if isinstance(v, dict) and v.get("score") is not None
    }
    if scored:
        sorted_scores = sorted(scored.items(), key=lambda x: x[1], reverse=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💪 강점 TOP 2")
            for cat, sc in sorted_scores[:2]:
                st.success(f"{cat}: {sc}/10")
        with col2:
            st.subheader("⚠️ 개선 필요 TOP 2")
            for cat, sc in sorted_scores[-2:]:
                st.error(f"{cat}: {sc}/10")

    st.divider()

    # ── 리포트 다운로드 ──
    st.subheader("💾 리포트 저장")
    report_text = generate_report(company_name, analysis)
    saved_path = save_report(company_name, report_text)

    with open(saved_path, "r", encoding="utf-8") as f:
        st.download_button(
            label="📄 리포트 다운로드 (.txt)",
            data=f.read(),
            file_name=os.path.basename(saved_path),
            mime="text/plain",
            use_container_width=True
        )