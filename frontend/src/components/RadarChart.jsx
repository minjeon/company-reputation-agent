import {
  Radar, RadarChart as RechartsRadar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from "recharts"

function RadarChart({ analysis }) {
  const data = Object.entries(analysis)
    .filter(([, v]) => v?.score !== null && v?.score !== undefined)
    .map(([category, v]) => ({
      category,
      score: v.score,
    }))

  return (
    <ResponsiveContainer width="100%" height={350}>
      <RechartsRadar data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="category" tick={{ fontSize: 13 }} />
        <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fontSize: 11 }} />
        <Radar
          dataKey="score"
          stroke="#4299e1"
          fill="#4299e1"
          fillOpacity={0.3}
        />
      </RechartsRadar>
    </ResponsiveContainer>
  )
}

export default RadarChart