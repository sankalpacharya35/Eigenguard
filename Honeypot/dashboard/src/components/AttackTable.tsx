// dashboard/src/components/AttackTable.tsx
import type { Attack } from "../types/Attack"
import { format } from "date-fns"

export default function AttackTable({ attacks }: { attacks: Attack[] }) {
  const formatDuration = (us: number) => {
    if (us < 1000) return `${us}μs`
    if (us < 1_000_000) return `${(us / 1000).toFixed(1)}ms`
    return `${(us / 1_000_000).toFixed(2)}s`
  }

  const formatBytesPerSec = (bps: number) => {
    if (bps < 1024) return `${bps.toFixed(0)} B/s`
    if (bps < 1024 * 1024) return `${(bps / 1024).toFixed(1)} KB/s`
    return `${(bps / (1024 * 1024)).toFixed(2)} MB/s`
  }

  return (
    <div className="max-h-96 overflow-y-auto border border-gray-700 rounded-lg">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-gray-900 border-b border-gray-700">
          <tr>
            <th className="text-left p-3">Time</th>
            <th className="text-left p-3">IP:Port</th>
            <th className="text-left p-3">Location</th>
            <th className="text-left p-3">Credentials</th>
            <th className="text-center p-3">Duration</th>
            <th className="text-center p-3">Fwd/Bwd Pkts</th>
            <th className="text-center p-3">Flow Rate</th>
            <th className="text-center p-3">Avg Pkt Size</th>
            <th className="text-center p-3">Flags</th>
          </tr>
        </thead>
        <tbody>
          {attacks.length === 0 ? (
            <tr>
              <td colSpan={9} className="text-center py-8 text-gray-500">
                No attacks recorded yet...
              </td>
            </tr>
          ) : (
            attacks.map((a) => (
              <tr
                key={a.id}
                className="border-t border-gray-800 hover:bg-gray-800 transition-colors"
              >
                <td className="p-3 font-medium">
                  {format(new Date(a.timestamp), "HH:mm:ss")}
                </td>
                <td className="p-3 font-mono text-cyan-400">
                  {a.src_ip}:{a.src_port}
                </td>
                <td className="p-3">
                  {a.country} ({a.city})
                </td>
                <td className="p-3 font-mono text-red-400">
                  {a.username}:{a.password}
                </td>
                <td className="p-3 text-center text-yellow-300">
                  {formatDuration(a.flow_duration)}
                </td>
                <td className="p-3 text-center font-mono">
                  {a.total_fwd_packets} → {a.total_backward_packets}
                </td>
                <td className="p-3 text-center text-orange-300">
                  {formatBytesPerSec(a.flow_bytes_s)}
                </td>
                <td className="p-3 text-center font-mono text-green-400">
                  {a.average_packet_size.toFixed(0)}B
                </td>
                <td className="p-3 text-center text-xs">
                  {a.syn_flag_count > 0 && <span className="text-blue-400">SYN </span>}
                  {a.psh_flag_count > 0 && <span className="text-purple-400">PSH </span>}
                  {a.ack_flag_count > 0 && <span className="text-gray-400">ACK </span>}
                  {a.fin_flag_count > 0 && <span className="text-red-500">FIN</span>}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}