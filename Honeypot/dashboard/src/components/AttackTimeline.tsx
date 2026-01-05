// dashboard/src/components/AttackTimeline.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import type { Attack } from "../types/Attack"

interface TimelineProps {
  attacks: Attack[]
}

export default function AttackTimeline({ attacks }: TimelineProps) {
  // Group by hour for the last 24 hours
  const now = new Date()
  const last24Hours = new Date(now.getTime() - 24 * 60 * 60 * 1000)
  
  const hourlyData = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date(now)
    hour.setHours(hour.getHours() - (23 - i))
    hour.setMinutes(0, 0, 0)
    
    const count = attacks.filter(a => {
      const attackTime = new Date(a.timestamp)
      return attackTime >= hour && attackTime < new Date(hour.getTime() + 60*60*1000)
    }).length
    
    return {
      time: hour.toLocaleTimeString('en-US', { hour: 'numeric' }),
      attacks: count
    }
  })

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
      <h3 className="text-xl font-bold mb-4 text-white">Attack Timeline (Last 24h)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={hourlyData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="time" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip 
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151" }}
            labelStyle={{ color: "#e5e7eb" }}
          />
          <Line 
            type="monotone" 
            dataKey="attacks" 
            stroke="#ef4444" 
            strokeWidth={3}
            dot={{ fill: '#ef4444', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}