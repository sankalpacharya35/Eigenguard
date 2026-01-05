// dashboard/src/app.tsx
import { useEffect, useState } from "react"
import AttackTable from "./components/AttackTable"
import CountryMap from "./components/CountryMap"
import StatsCards from "./components/StatsCards"
import AttackTimeline from "./components/AttackTimeline"
import TopCredentials from "./components/TopCredentials"
import type { Attack } from "./types/Attack"

interface Stats {
  total_attacks: number
  today_attacks: number
  unique_ips: number
  top_countries: { name: string; count: number }[]
  avg_flow_duration: number
  max_flow_rate: number
  avg_packet_size: number
  most_common_username: string
}

export default function App() {
  const [attacks, setAttacks] = useState<Attack[]>([])
  const [stats, setStats] = useState<Stats | null>(null)

  const defaultStats: Stats = {
    total_attacks: 0,
    today_attacks: 0,
    unique_ips: 0,
    top_countries: [],
    avg_flow_duration: 0,
    max_flow_rate: 0,
    avg_packet_size: 0,
    most_common_username: ""
  }
const fetchData = async () => {
  try {
    const [attacksRes, statsRes] = await Promise.all([
      fetch("http://localhost:8000/api/attacks"),
      fetch("http://localhost:8000/api/stats")
    ])

    if (!attacksRes.ok || !statsRes.ok) {
      console.error("API responded with error:", attacksRes.status, statsRes.status)
      return
    }

    const attacksData = await attacksRes.json()
    const statsData = await statsRes.json()

    console.log(`Fetched ${attacksData.length} attacks`)  // You will see this in console
    setAttacks(attacksData)
    setStats(statsData)
  } catch (err) {
    console.error("Fetch failed completely:", err)
  }
}

useEffect(() => {
  fetchData()  // Initial load
  const interval = setInterval(() => {
    fetchData()
  }, 3000)  // Every 3 seconds — fast enough for demo

  return () => clearInterval(interval)
}, [])

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <header>
        <div className="text-center">
          <h1 className="text-3xl font-bold">SSH Honeypot Dashboard</h1>
          <p className="text-center text-gray-400 mt-4 text-lg">
            Real-time brute-force attack monitoring with flow analysis
          </p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto space-y-8">
        <StatsCards stats={stats || defaultStats} />

        <div className="grid md:grid-cols-2 gap-8">
          <AttackTimeline attacks={attacks} />
          <CountryMap attacks={attacks} />
        </div>

        <TopCredentials attacks={attacks} />

        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Recent Attacks</h2>
          <a
            href="/api/export-csv"
            className="bg-green-800 hover:bg-green-700 px-6 py-3 rounded-lg font-medium transition"
          >
            Export to CSV
          </a>
        </div>

        <AttackTable attacks={attacks.slice(0, 50)} />
      </div>
    </div>
  )
}