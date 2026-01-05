// dashboard/src/components/StatsCards.tsx
import type { Attack } from "../types/Attack"

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

export default function StatsCards({ stats }: { stats: Stats }) {
  if (!stats.total_attacks) {
    return <div className="text-center py-10 text-gray-400">Loading stats...</div>
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
      <div className="bg-red-900/50 border border-red-800 rounded-lg p-6">
        <div className="text-4xl font-bold text-red-400">{stats.today_attacks}</div>
        <div className="text-gray-300 mt-1">Attacks Today</div>
      </div>

      <div className="bg-orange-900/50 border border-orange-800 rounded-lg p-6">
        <div className="text-4xl font-bold text-orange-400">{stats.total_attacks}</div>
        <div className="text-gray-300 mt-1">Total Attacks</div>
      </div>

      <div className="bg-purple-900/50 border border-purple-800 rounded-lg p-6">
        <div className="text-3xl font-bold text-purple-300">
          {(stats.max_flow_rate / 1024 / 1024).toFixed(2)} MB/s
        </div>
        <div className="text-gray-300 mt-1">Peak Flow Rate</div>
      </div>

      <div className="bg-cyan-900/50 border border-cyan-800 rounded-lg p-6">
        <div className="text-4xl font-bold text-cyan-400">{stats.unique_ips}</div>
        <div className="text-gray-300 mt-1">Unique Attackers</div>
      </div>

      <div className="bg-yellow-900/50 border border-yellow-800 rounded-lg p-6">
        <div className="text-3xl font-bold text-yellow-300">
          {stats.avg_packet_size.toFixed(0)}B
        </div>
        <div className="text-gray-300 mt-1">Avg Packet Size</div>
      </div>

      <div className="bg-green-900/50 border border-green-800 rounded-lg p-6">
        <div className="text-4xl font-bold text-green-400">
          {stats.top_countries[0]?.count || 0}
        </div>
        <div className="text-gray-300 mt-1">
          Top: {stats.top_countries[0]?.name || "N/A"}
        </div>
      </div>

      <div className="bg-indigo-900/50 border border-indigo-800 rounded-lg p-6">
        <div className="text-3xl font-bold text-indigo-300">
          {(stats.avg_flow_duration / 1_000_000).toFixed(2)}s
        </div>
        <div className="text-gray-300 mt-1">Avg Duration</div>
      </div>

      <div className="bg-pink-900/50 border border-pink-800 rounded-lg p-6">
        <div className="text-3xl font-bold text-pink-400">
          {stats.most_common_username}
        </div>
        <div className="text-gray-300 mt-1">Top Username</div>
      </div>
    </div>
  )
}