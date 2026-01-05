// dashboard/src/components/TopCredentials.tsx
import type { Attack } from "../types/Attack"

interface TopCredsProps {
  attacks: Attack[]
}

export default function TopCredentials({ attacks }: TopCredsProps) {
  const usernameCount = attacks.reduce((acc, a) => {
    acc[a.username] = (acc[a.username] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const passwordCount = attacks.reduce((acc, a) => {
    acc[a.password] = (acc[a.password] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const topUsernames = Object.entries(usernameCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 8)

  const topPasswords = Object.entries(passwordCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 8)

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-bold mb-4 text-red-400">Most Targeted Usernames</h3>
        <div className="space-y-3">
          {topUsernames.map(([user, count]: [string, number]) => (
            <div key={user} className="flex justify-between items-center">
              <span className="font-mono text-cyan-300">{user}</span>
              <span className="text-2xl font-bold text-red-400">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-bold mb-4 text-orange-400">Most Used Passwords</h3>
        <div className="space-y-3">
          {topPasswords.map(([passw, count]: [string, number]) => (
            <div key={passw} className="flex justify-between items-center">
              <span className="font-mono text-yellow-300">{passw}</span>
              <span className="text-2xl font-bold text-orange-400">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}