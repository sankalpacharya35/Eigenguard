# backend/app.py
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from ml.feature_extract import honeypot_logs_to_features
from ml.predictor import Predictor, single_predict
import threading
import json
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "honeypot.db")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "ddos_rf.joblib")

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend")
CORS(app)

# load model at startup if exists
predictor = None
if os.path.exists(MODEL_PATH):
    try:
        predictor = Predictor(MODEL_PATH)
        app.logger.info("Predictor loaded.")
    except Exception as e:
        app.logger.warning("Failed to load predictor: %s", e)

# in-memory blocked IP cache for fast check
blocked_ips = set()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def log_attack(endpoint, details):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (timestamp, endpoint, ip, user_agent, headers, body) VALUES (?, ?, ?, ?, ?, ?)",
        (
            datetime.utcnow().isoformat(),
            endpoint,
            details.get("ip"),
            details.get("user_agent"),
            details.get("headers"),
            details.get("body"),
        ),
    )
    conn.commit()
    conn.close()

def add_block(ip, reason="ml_detected", score=1.0):
    if not ip:
        return
    if ip in blocked_ips:
        return
    blocked_ips.add(ip)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO blocked_ips (ip, reason, score, blocked_at)
        VALUES (?, ?, ?, ?)
    """, (ip, reason, float(score), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    app.logger.warning(f"Blocked IP {ip} reason={reason} score={score}")

# Reject requests from blocked IPs
@app.before_request
def check_block():
    ip = request.remote_addr
    if ip in blocked_ips:
        abort(403)

# Serve frontend
@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

@app.route('/admin', methods=['GET'])
def fake_admin_page():
    return send_from_directory('../frontend', 'admin.html')

@app.route('/fake_login', methods=['POST'])
def fake_login():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')
    headers = dict(request.headers)
    try:
        creds = request.get_json(silent=True) or request.form.to_dict() or {}
    except Exception:
        creds = {}
    body = json.dumps(creds)

    log_attack('/fake_login', {
        "ip": ip,
        "user_agent": ua,
        "headers": json.dumps(headers),
        "body": body
    })

    # After logging, run asynchronous analysis/prediction on this IP's recent window
    threading.Thread(target=analyze_ip_recent, args=(ip,)).start()

    return jsonify({"status": "invalid", "message": "Invalid credentials"}), 401

@app.route('/fake_api/<path:anypath>', methods=['GET','POST','PUT','DELETE'])
def fake_api(anypath):
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')
    headers = dict(request.headers)
    body = request.get_data(as_text=True)

    log_attack(f'/fake_api/{anypath}', {
        "ip": ip,
        "user_agent": ua,
        "headers": json.dumps(headers),
        "body": body
    })

    threading.Thread(target=analyze_ip_recent, args=(ip,)).start()

    return jsonify({"error": "Not found", "path": anypath}), 404

# Dashboard APIs
@app.route('/api/logs', methods=['GET'])
def api_logs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, endpoint, ip, user_agent, headers, body FROM logs ORDER BY id DESC LIMIT 500")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/logs/count', methods=['GET'])
def api_logs_count():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM logs")
    cnt = cur.fetchone()[0]
    conn.close()
    return jsonify({"count": cnt})

# blocked ip endpoints
@app.route('/api/blocked', methods=['GET'])
def api_blocked_list():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT ip, reason, score, blocked_at FROM blocked_ips ORDER BY blocked_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/unblock', methods=['POST'])
def api_unblock():
    data = request.get_json() or {}
    ip = data.get('ip')
    if not ip:
        return jsonify({"error":"missing ip"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))
    conn.commit()
    conn.close()
    blocked_ips.discard(ip)
    return jsonify({"status":"ok"})

@app.route('/dashboard')
def dashboard_page():
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

# === Analysis / Prediction ===
def analyze_ip_recent(ip, window_seconds=300, prob_threshold=0.7):
    """
    Convert recent logs for this IP into features and run predictor.
    If probability >= prob_threshold -> block.
    """
    if predictor is None:
        app.logger.info("No predictor available; skipping ML analyze.")
        return

    try:
        conn = get_db()
        cur = conn.cursor()
        # fetch recent logs (last window_seconds*2 sec)
        cur.execute("SELECT timestamp, endpoint, ip, user_agent, headers, body FROM logs WHERE ip=? ORDER BY id DESC LIMIT 200", (ip,))
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return
        # make DataFrame-like structure
        import pandas as pd
        recs = []
        for r in rows:
            recs.append({
                'timestamp': r['timestamp'],
                'endpoint': r['endpoint'],
                'ip': r['ip'],
                'user_agent': r['user_agent'],
                'headers': r['headers'],
                'body': r['body']
            })
        df = pd.DataFrame(recs)
        feat_df = honeypot_logs_to_features(df, window_seconds=window_seconds)
        if feat_df.empty:
            return
        probs = predictor.predict_proba(feat_df)
        max_prob = float(probs.max())
        app.logger.info(f"ML probs for ip={ip} max_prob={max_prob:.3f}")
        # choose to block if any window has high probability
        if max_prob >= prob_threshold:
            add_block(ip, reason="ml_detected", score=max_prob)
            # optional: call system firewall here (commented)
            # import subprocess
            # subprocess.run(['sudo','iptables','-A','INPUT','-s', ip, '-j', 'DROP'])
            # send alert (placeholder - you can integrate email/telegram)
            app.logger.warning(f"IP {ip} blocked by ML (prob={max_prob:.3f})")
    except Exception as e:
        app.logger.error("analyze_ip_recent error: %s", e)

if __name__ == '__main__':
    # preload blocked IPs from DB into memory
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT ip FROM blocked_ips")
        for r in cur.fetchall():
            blocked_ips.add(r[0])
        conn.close()
    except Exception:
        pass

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
