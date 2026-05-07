import { useState } from "react"

function AgentLogs({ logs }) {
  const [open, setOpen] = useState(false)

  if (!logs || logs.length === 0) return null

  return (
    <div style={{
      background: "#1a202c", borderRadius: 12,
      padding: 20, marginBottom: 24, color: "#68d391"
    }}>
      <div
        onClick={() => setOpen(!open)}
        style={{ cursor: "pointer", display: "flex", justifyContent: "space-between" }}
      >
        <span style={{ fontWeight: 700 }}>🤖 AI 수집 과정 보기</span>
        <span>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div style={{ marginTop: 12 }}>
          {logs.map((log, i) => (
            <div key={i} style={{
              fontFamily: "monospace", fontSize: 13,
              padding: "4px 0", borderBottom: "1px solid #2d3748"
            }}>
              ✅ {log}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AgentLogs