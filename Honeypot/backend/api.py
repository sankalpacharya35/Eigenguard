# backend/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, Attack
from sqlalchemy import inspect
from datetime import datetime
from collections import Counter
import csv
from fastapi.responses import StreamingResponse
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← This allows localhost:5173 (and everything) — perfect for dev!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

@app.get("/")
def read_root():
    return {"message": "Honeypot API Running!"}

@app.get("/api/attacks")
def get_attacks():
    session = SessionLocal()
    try:
        attacks = session.query(Attack).order_by(Attack.timestamp.desc()).limit(500).all()
        result = [object_as_dict(a) for a in attacks]
    finally:
        session.close()
    return result

@app.get("/api/stats")
def get_stats():
    session = SessionLocal()
    try:
        attacks = session.query(Attack).all()
    finally:
        session.close()

    if not attacks:
        return {
            "total_attacks": 0,
            "today_attacks": 0,
            "unique_ips": 0,
            "top_countries": [],
            "avg_flow_duration": 0,
            "max_flow_rate": 0,
            "avg_packet_size": 0,
            "most_common_username": "N/A"
        }

    today = datetime.utcnow().date()
    today_attacks = sum(1 for a in attacks if a.timestamp.date() == today)
    unique_ips = len({a.src_ip for a in attacks})

    country_counter = Counter(a.country for a in attacks if a.country)
    top_countries = [{"name": c or "Unknown", "count": n} for c, n in country_counter.most_common(5)]

    avg_duration = sum(a.flow_duration or 0 for a in attacks) / len(attacks)
    max_rate = max((a.flow_bytes_s or 0 for a in attacks), default=0)
    avg_pkt = sum(a.average_packet_size or 0 for a in attacks) / len(attacks)

    user_counter = Counter(a.username for a in attacks)
    top_user = user_counter.most_common(1)[0][0] if user_counter else "N/A"

    return {
        "total_attacks": len(attacks),
        "today_attacks": today_attacks,
        "unique_ips": unique_ips,
        "top_countries": top_countries,
        "avg_flow_duration": avg_duration,
        "max_flow_rate": max_rate,
        "avg_packet_size": avg_pkt,
        "most_common_username": top_user
    }

@app.get("/api/export-csv")
def export_csv():
    session = SessionLocal()
    try:
        attacks = session.query(Attack).order_by(Attack.timestamp.desc()).all()
    finally:
        session.close()

    if not attacks:
        return {"message": "No data to export"}

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=object_as_dict(attacks[0]).keys())
    writer.writeheader()
    for a in attacks:
        writer.writerow(object_as_dict(a))

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attacks.csv"}
    )