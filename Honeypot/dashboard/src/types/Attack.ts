// dashboard/src/types/Attack.ts
export interface Attack {
  id: number
  timestamp: string
  src_ip: string
  src_port: number
  username: string
  password: string
  command: string | null

  country: string
  country_code: string
  city: string
  latitude: number | null
  longitude: number | null

  // === NEW: CIC Flow Features ===
  destination_port: number
  flow_duration: number  // microseconds
  total_fwd_packets: number
  total_backward_packets: number
  total_length_fwd_packets: number
  total_length_bwd_packets: number

  fwd_packet_length_max: number
  fwd_packet_length_mean: number
  fwd_packet_length_std: number

  bwd_packet_length_max: number
  bwd_packet_length_mean: number
  bwd_packet_length_std: number

  flow_bytes_s: number
  flow_packets_s: number

  flow_iat_mean: number
  flow_iat_std: number
  flow_iat_max: number

  fwd_iat_mean: number
  fwd_iat_std: number
  bwd_iat_mean: number
  bwd_iat_std: number

  syn_flag_count: number
  ack_flag_count: number
  psh_flag_count: number
  fin_flag_count: number

  down_up_ratio: number
  average_packet_size: number
  avg_fwd_segment_size: number
  avg_bwd_segment_size: number

  protocol: number
  packet_length_mean: number
  packet_length_std: number

  label: string
}