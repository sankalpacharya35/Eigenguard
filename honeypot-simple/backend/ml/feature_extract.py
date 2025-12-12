# backend/ml/feature_extract.py
import pandas as pd
import numpy as np
from datetime import datetime

# === Configuration: features we will use from CICDDoS2019-ish flows ===
FEATURE_COLS = [
    'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
    'Fwd Packet Length Mean', 'Bwd Packet Length Mean',
    'Flow IAT Mean', 'Flow Bytes/s', 'Flow Packets/s'
]

# --- Load and preprocess CICDDoS2019 CSV ---
def load_cicddos(csv_path):
    """
    Loads a CICDDoS2019 CSV and returns DataFrame with chosen features and label (Attack)
    Note: depends on CSV having matching column names; adjust names if different.
    """
    df = pd.read_csv(csv_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    # Filter out rows without Label
    df = df[df['Label'].notna()]
    # Map to binary label
    df['Attack'] = df['Label'].apply(lambda x: 0 if 'Benign' in str(x) else 1)
    # Keep only features present in file
    available = [c for c in FEATURE_COLS if c in df.columns]
    # Fill NA numeric with 0
    df_feat = df[available].fillna(0)
    df_feat['Attack'] = df['Attack']
    return df_feat

# --- Convert honeypot logs (raw) into flow features by IP/time window ---
def honeypot_logs_to_features(df_logs, window_seconds=300):
    """
    df_logs: DataFrame with columns: timestamp (ISO str), ip, endpoint, user_agent, headers, body
    Returns DataFrame with features roughly aligned to FEATURE_COLS.
    Approach: group by (ip, window) where window is floor(timestamp / window_seconds)
    """
    if df_logs.empty:
        return pd.DataFrame(columns=FEATURE_COLS + ['Attack'])

    df = df_logs.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    epoch = pd.Timestamp("1970-01-01", tz=None)
    # compute window index
    df['window_idx'] = (df['timestamp'].astype('int64') // 10**9) // window_seconds

    records = []
    groups = df.groupby(['ip','window_idx'])
    for (ip,widx), g in groups:
        first = g['timestamp'].min()
        last = g['timestamp'].max()
        duration = max((last - first).total_seconds(), 1.0)
        req_count = len(g)
        unique_endpoints = g['endpoint'].nunique()
        avg_body_len = g['body'].astype(str).map(len).mean()
        # Approximations to flow features:
        flow_bytes = g['body'].astype(str).map(len).sum()
        fwd_pkts = req_count  # approximate
        bwd_pkts = 0  # we don't capture server responses easily
        fwd_len_mean = g['body'].astype(str).map(len).mean()
        bwd_len_mean = 0.0
        flow_iat_mean = duration / req_count if req_count>0 else duration
        flow_bps = flow_bytes / duration
        flow_pps = req_count / duration

        rec = {
            'Flow Duration': duration,
            'Total Fwd Packets': fwd_pkts,
            'Total Backward Packets': bwd_pkts,
            'Total Length of Fwd Packets': flow_bytes,
            'Total Length of Bwd Packets': 0,
            'Fwd Packet Length Mean': fwd_len_mean,
            'Bwd Packet Length Mean': bwd_len_mean,
            'Flow IAT Mean': flow_iat_mean,
            'Flow Bytes/s': flow_bps,
            'Flow Packets/s': flow_pps,
            'Attack': 1  # honeypot hits are labelled attack for training/fine-tuning
        }
        records.append(rec)

    out = pd.DataFrame(records)
    # ensure all FEATURE_COLS exist
    for c in FEATURE_COLS:
        if c not in out.columns:
            out[c] = 0.0
    return out[FEATURE_COLS + ['Attack']]
