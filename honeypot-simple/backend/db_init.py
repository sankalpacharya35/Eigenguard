import sqlite3

conn = sqlite3.connect("honeypot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    ip TEXT,
    method TEXT,
    path TEXT,
    user_agent TEXT,
    body TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id INTEGER,
    req_rate INTEGER,
    body_size INTEGER,
    header_count INTEGER,
    has_sql INTEGER,
    has_cmd INTEGER
)
""")

conn.commit()
conn.close()
