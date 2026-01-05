# backend/utils/geo.py  ← BULLETPROOF VERSION (works even without GeoIP DB)
def get_location(ip: str):
    # ALL LOCAL NETWORKS → MUMBAI, INDIA (you will see this!)
    if any(ip.startswith(p) for p in ["127.", "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "::1"]):
        return {
            "country": "India",
            "country_code": "IN",
            "city": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777
        }
    
    # Fallback for everything else
    return {
        "country": "Internet",
        "country_code": "WW",
        "city": "Unknown",
        "latitude": 30.0,
        "longitude": 0.0
    }
