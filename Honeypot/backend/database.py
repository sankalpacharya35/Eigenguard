from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    src_ip = Column(String, index=True)
    src_port = Column(Integer)

    username = Column(String)
    password = Column(String)
    command = Column(Text, nullable=True)

    country = Column(String)
    country_code = Column(String)
    city = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # === CIC Flow Features - MUST MATCH EXACTLY WHAT WE PASS IN honeypot.py ===
    destination_port = Column(Integer, default=2222)
    flow_duration = Column(Float, default=0.0)  # microseconds
    total_fwd_packets = Column(Integer, default=0)
    total_backward_packets = Column(Integer, default=0)        # ← was total_bwd_packets?
    total_length_fwd_packets = Column(Integer, default=0)
    total_length_bwd_packets = Column(Integer, default=0)

    fwd_packet_length_max = Column(Float, default=0.0)
    fwd_packet_length_mean = Column(Float, default=0.0)
    fwd_packet_length_std = Column(Float, default=0.0)

    bwd_packet_length_max = Column(Float, default=0.0)
    bwd_packet_length_mean = Column(Float, default=0.0)
    bwd_packet_length_std = Column(Float, default=0.0)

    flow_bytes_s = Column(Float, default=0.0)
    flow_packets_s = Column(Float, default=0.0)

    flow_iat_mean = Column(Float, default=0.0)
    flow_iat_std = Column(Float, default=0.0)
    flow_iat_max = Column(Float, default=0.0)

    fwd_iat_mean = Column(Float, default=0.0)
    fwd_iat_std = Column(Float, default=0.0)
    fwd_iat_max = Column(Float, default=0.0)

    bwd_iat_mean = Column(Float, default=0.0)
    bwd_iat_std = Column(Float, default=0.0)
    bwd_iat_max = Column(Float, default=0.0)

    syn_flag_count = Column(Integer, default=0)
    ack_flag_count = Column(Integer, default=0)
    psh_flag_count = Column(Integer, default=0)
    fin_flag_count = Column(Integer, default=0)

    down_up_ratio = Column(Float, default=0.0)
    average_packet_size = Column(Float, default=0.0)
    avg_fwd_segment_size = Column(Float, default=0.0)
    avg_bwd_segment_size = Column(Float, default=0.0)

    protocol = Column(Integer, default=6)
    packet_length_mean = Column(Float, default=0.0)
    packet_length_std = Column(Float, default=0.0)
    packet_length_variance = Column(Float, default=0.0)

    label = Column(String, default="SSH-BruteForce")

# THIS LINE RECREATES THE TABLE WITH NEW SCHEMA
Base.metadata.create_all(bind=engine)
print("Database initialized with full CIC flow features!")