import { useState } from "react"
import axios from "axios"
import SearchBar from "./components/SearchBar"
import RadarChart from "./components/RadarChart"
import ResultCard from "./components/ResultCard"
import AgentLogs from "./components/AgentLogs"
import "./index.css"

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async (companyName) => {
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await axios.post("http://localhost:8000/api/analyze", {
        company_name: companyName,
      })
      setResult(response.data)
    } catch (err) {
      setError("분석 중 오류가 발생했습니다. 다시 시도해주세요.")
    } finally {
      setLoading(false)
    }
  }

  // 평균 점수 계산
  const getAvgScore = (analysis) => {
    const scores = Object.values(analysis)
      .filter((v) => v?.score !== null && v?.score !== undefined)
      .map((v) => v.score)
    if (scores.length === 0) return null
    return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
  }

  const getScoreLabel = (score) => {
    if (score === null) return "정보 없음"
    if (score >= 8) return "✅ 우수"
    if (score >= 6) return "🔵 양호"
    if (score >= 4) return "🟡 보통"
    return "🔴 미흡"
  }

  return (
    <div style={{ minHeight: "100vh", padding: "40px 20px" }}>
      <div style={{ maxWidth: 900, margin: "0 auto" }}>

        {/* 헤더 */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <h1 style={{ fontSize: 32, fontWeight: 800, color: "#1a1a2e" }}>
            🏢 기업 평판 분석 에이전트
          </h1>
          <p style={{ color: "#666", marginTop: 8 }}>
            회사명을 입력하면 AI가 웹/뉴스/리뷰를 수집해서 분석해드려요
          </p>
        </div>

        {/* 검색창 */}
        <SearchBar onAnalyze={handleAnalyze} loading={loading} />

        {/* 로딩 */}
        {loading && (
          <div style={{ textAlign: "center", padding: 60 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
            <p style={{ fontSize: 18, color: "#555" }}>
              AI가 정보를 수집하고 분석 중이에요...
            </p>
            <p style={{ fontSize: 14, color: "#999", marginTop: 8 }}>
              보통 30초~1분 정도 소요돼요
            </p>
          </div>
        )}

        {/* 에러 */}
        {error && (
          <div style={{
            background: "#fff0f0", border: "1px solid #ffcccc",
            borderRadius: 12, padding: 20, textAlign: "center", color: "#e53e3e"
          }}>
            {error}
          </div>
        )}

        {/* 결과 */}
        {result && (
          <div>
            {/* 에이전트 로그 */}
            <AgentLogs logs={result.agent_logs} />

            {/* 종합 점수 */}
            <div style={{
              background: "white", borderRadius: 16, padding: 32,
              marginBottom: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>
                📊 종합 점수
              </h2>
              <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 48, fontWeight: 900, color: "#4299e1" }}>
                    {getAvgScore(result.analysis)}
                  </div>
                  <div style={{ color: "#666", fontSize: 14 }}>/ 10</div>
                </div>
                <div>
                  <div style={{ fontSize: 24 }}>
                    {getScoreLabel(parseFloat(getAvgScore(result.analysis)))}
                  </div>
                  <div style={{ color: "#888", fontSize: 14, marginTop: 4 }}>
                    {result.company_name} 평판 분석 결과
                  </div>
                </div>
              </div>
            </div>

            {/* 레이더 차트 */}
            <div style={{
              background: "white", borderRadius: 16, padding: 32,
              marginBottom: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>
                📡 카테고리별 점수 분포
              </h2>
              <RadarChart analysis={result.analysis} />
            </div>

            {/* 카테고리별 상세 */}
            <div style={{
              background: "white", borderRadius: 16, padding: 32,
              marginBottom: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>
                📋 카테고리별 상세 분석
              </h2>
              {Object.entries(result.analysis).map(([category, data]) => (
                <ResultCard key={category} category={category} data={data} />
              ))}
            </div>

            {/* 강점 / 약점 */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {(() => {
                const scored = Object.entries(result.analysis)
                  .filter(([, v]) => v?.score !== null && v?.score !== undefined)
                  .sort(([, a], [, b]) => b.score - a.score)
                return (
                  <>
                    <div style={{
                      background: "#f0fff4", borderRadius: 16, padding: 24,
                      border: "1px solid #9ae6b4"
                    }}>
                      <h3 style={{ color: "#276749", marginBottom: 12 }}>💪 강점 TOP 2</h3>
                      {scored.slice(0, 2).map(([cat, v]) => (
                        <div key={cat} style={{
                          background: "#c6f6d5", borderRadius: 8,
                          padding: "8px 12px", marginBottom: 8, fontWeight: 600
                        }}>
                          {cat}: {v.score}/10
                        </div>
                      ))}
                    </div>
                    <div style={{
                      background: "#fff5f5", borderRadius: 16, padding: 24,
                      border: "1px solid #feb2b2"
                    }}>
                      <h3 style={{ color: "#c53030", marginBottom: 12 }}>⚠️ 개선 필요 TOP 2</h3>
                      {scored.slice(-2).reverse().map(([cat, v]) => (
                        <div key={cat} style={{
                          background: "#fed7d7", borderRadius: 8,
                          padding: "8px 12px", marginBottom: 8, fontWeight: 600
                        }}>
                          {cat}: {v.score}/10
                        </div>
                      ))}
                    </div>
                  </>
                )
              })()}
            </div>
            <div style={{
              background: "white", borderRadius: 16, padding: 32,
              marginTop: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
              textAlign: "center"
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 16 }}>
                💾 리포트 저장
              </h2>
              <button
                onClick={async () => {
                  try {
                    const response = await axios.get(
                      `http://localhost:8000/api/report/${encodeURIComponent(result.company_name)}`,
                      { responseType: "blob" }
                    )
                    const url = window.URL.createObjectURL(new Blob([response.data]))
                    const link = document.createElement("a")
                    link.href = url
                    link.setAttribute("download", `${result.company_name}_reputation.txt`)
                    document.body.appendChild(link)
                    link.click()
                    link.remove()
                  } catch {
                    alert("리포트 다운로드에 실패했습니다.")
                  }
                }}
                style={{
                  padding: "14px 40px", fontSize: 16, fontWeight: 700,
                  borderRadius: 12, border: "none", cursor: "pointer",
                  background: "#4299e1", color: "white",
                }}
              >
                📄 리포트 다운로드 (.txt)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App