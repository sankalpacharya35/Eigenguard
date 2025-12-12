# backend/db_init.py
import sqlite3, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "honeypot.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    endpoint TEXT,
    ip TEXT,
    user_agent TEXT,
    headers TEXT,
    body TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS blocked_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT UNIQUE,
    reason TEXT,
    score REAL,
    blocked_at TEXT
)
""")
conn.commit()
conn.close()
print("DB initialized at", DB_PATH)
