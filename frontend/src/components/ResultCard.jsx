import { useState } from "react"

const getScoreColor = (score) => {
  if (score === null) return "#a0aec0"
  if (score >= 8) return "#48bb78"
  if (score >= 6) return "#4299e1"
  if (score >= 4) return "#ed8936"
  return "#f56565"
}

const getScoreLabel = (score) => {
  if (score === null) return "정보 없음"
  if (score >= 8) return "✅ 우수"
  if (score >= 6) return "🔵 양호"
  if (score >= 4) return "🟡 보통"
  return "🔴 미흡"
}

function ResultCard({ category, data }) {
  const [open, setOpen] = useState(false)
  const score = data?.score ?? null
  const color = getScoreColor(score)

  return (
    <div style={{
      border: "1px solid #e2e8f0", borderRadius: 12,
      marginBottom: 12, overflow: "hidden"
    }}>
      {/* 헤더 */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          display: "flex", alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 20px", cursor: "pointer",
          background: open ? "#f7fafc" : "white",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 10,
            background: color, display: "flex",
            alignItems: "center", justifyContent: "center",
            color: "white", fontWeight: 900, fontSize: 18
          }}>
            {score ?? "-"}
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>{category}</div>
            <div style={{ color: "#666", fontSize: 13 }}>{getScoreLabel(score)}</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {data?.positive_count !== undefined && (
            <div style={{ fontSize: 13, color: "#666" }}>
              <span style={{ color: "#48bb78", fontWeight: 600 }}>
                긍정 {data.positive_count}
              </span>
              {" / "}
              <span style={{ color: "#f56565", fontWeight: 600 }}>
                부정 {data.negative_count}
              </span>
            </div>
          )}
          <div style={{ color: "#a0aec0" }}>{open ? "▲" : "▼"}</div>
        </div>
      </div>

      {/* 점수 바 */}
      <div style={{ height: 4, background: "#e2e8f0" }}>
        <div style={{
          height: "100%", width: `${(score ?? 0) * 10}%`,
          background: color, transition: "width 0.5s"
        }} />
      </div>

      {/* 상세 내용 */}
      {open && (
        <div style={{ padding: "16px 20px", background: "#f7fafc" }}>
          {data?.summary && (
            <p style={{ color: "#555", marginBottom: 12, lineHeight: 1.6 }}>
              {data.summary}
            </p>
          )}
          {data?.score_basis && (
            <div style={{
              background: "#edf2f7", borderRadius: 8,
              padding: "8px 12px", marginBottom: 12,
              fontSize: 13, color: "#4a5568"
            }}>
              📊 채점 근거: {data.score_basis}
            </div>
          )}
          {data?.evidence?.length > 0 && (
            <div>
              <div style={{ fontWeight: 600, marginBottom: 8, fontSize: 14 }}>
                근거 텍스트:
              </div>
              {data.evidence.map((e, i) => {
                const text = typeof e === "object" ? e.text : e
                const verified = typeof e === "object" ? e.verified : true
                return (
                  <div key={i} style={{
                    background: "white", borderRadius: 8,
                    padding: "8px 12px", marginBottom: 6,
                    fontSize: 13, color: "#555",
                    borderLeft: `3px solid ${verified ? "#4299e1" : "#a0aec0"}`
                  }}>
                    {verified ? "👌 ( 출처확인) " : "❓ ( 출처미확인 ) "} {text}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ResultCard