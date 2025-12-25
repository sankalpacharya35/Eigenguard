import os, sqlite3, json
from datetime import datetime
from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "honeypot.db")

app = Flask(__name__, static_folder="../frontend/static", static_url_path="/static")
CORS(app)

IGNORED_PREFIX = ("api", "static")
IGNORED_PATHS = ["/", "/favicon.ico"]

# ---------- DB ----------
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            endpoint TEXT,
            method TEXT,
            ip TEXT,
            user_agent TEXT,
            body TEXT,
            is_attack INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- LOGGING ----------
def log_request(endpoint, is_attack):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs
        (timestamp, endpoint, method, ip, user_agent, body, is_attack)
        VALUES (?,?,?,?,?,?,?)
    """, (
        datetime.utcnow().isoformat(),
        endpoint,
        request.method,
        request.remote_addr,
        request.headers.get("User-Agent", ""),
        request.get_data(as_text=True),
        is_attack
    ))
    conn.commit()
    conn.close()

# ---------- DASHBOARD ----------
@app.route("/")
def dashboard():
    return send_from_directory("../frontend", "index.html")

# ---------- API ----------
@app.route("/api/logs")
def all_logs():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 200")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/logs/attacks")
def attack_logs():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs WHERE is_attack=1 ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/logs/count")
def log_count():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM logs")
    count = cur.fetchone()[0]
    conn.close()
    return jsonify({"count": count})

# ---------- HONEYPOT (CATCH ALL) ----------
@app.route("/<path:path>", methods=["GET","POST","PUT","DELETE","PATCH"])
def honeypot(path):

    # do NOT log dashboard/api/static
    if path.startswith(IGNORED_PREFIX):
        abort(404)

    endpoint = "/" + path
    is_attack = endpoint not in IGNORED_PATHS

    log_request(endpoint, int(is_attack))

    return jsonify({
        "status": "logged",
        "endpoint": endpoint,
        "attack": is_attack
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
