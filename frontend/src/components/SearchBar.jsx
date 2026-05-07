import { useState } from "react"

function SearchBar({ onAnalyze, loading }) {
  const [input, setInput] = useState("")

  const handleSubmit = () => {
    if (!input.trim()) return
    onAnalyze(input.trim())
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit()
  }

  return (
    <div style={{ marginBottom: 32 }}>
      <div style={{ display: "flex", gap: 12 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="예: 카카오, 삼성전자, 네이버"
          disabled={loading}
          style={{
            flex: 1, padding: "16px 20px", fontSize: 16,
            borderRadius: 12, border: "2px solid #e2e8f0",
            outline: "none", background: "white",
            transition: "border 0.2s",
          }}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          style={{
            padding: "16px 32px", fontSize: 16, fontWeight: 700,
            borderRadius: 12, border: "none", cursor: "pointer",
            background: loading ? "#a0aec0" : "#4299e1",
            color: "white", transition: "background 0.2s",
          }}
        >
          {loading ? "분석 중..." : "🔍 분석 시작"}
        </button>
      </div>
    </div>
  )
}

export default SearchBar