import pandas as pd

def honeypot_logs_to_features(df, window_seconds=300):
    if df.empty:
        return pd.DataFrame()

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    duration = (df['timestamp'].max() - df['timestamp'].min()).total_seconds()
    duration = max(duration, 1)

    pkt_count = len(df)
    bytes_total = df['body'].fillna("").str.len().sum()
    header_bytes = df['headers'].fillna("").str.len().sum()

    features = {
        "flow_duration": duration,
        "total_packets": pkt_count,
        "packets_per_sec": pkt_count / duration,
        "bytes_per_sec": bytes_total / duration,
        "avg_packet_size": bytes_total / pkt_count if pkt_count else 0,
        "header_bytes": header_bytes,
        "unique_endpoints": df['endpoint'].nunique(),
        "unique_user_agents": df['user_agent'].nunique(),
    }

    return pd.DataFrame([features])
