#!/bin/bash
# ONE-CLICK HONEYPOT LAUNCHER — FIXED & OPTIMIZED
# Works perfectly on Kali Linux

echo "Starting Honeypot Project (API + Honeypot + Dashboard)"
echo ""

# Kill old processes safely
echo "Cleaning old processes..."
pkill -f "uvicorn.*api:app" 2>/dev/null || true
pkill -f "python.*honeypot.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*dashboard" 2>/dev/null || true
sleep 2

# Activate virtual environment (if you have one)
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

# Start FastAPI Backend with uvicorn
echo "Starting API on http://localhost:8000"
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload > ../api.log 2>&1 &
API_PID=$!
echo "API started (PID: $API_PID)"
sleep 4  # Give it time to start

# Start Honeypot
echo "Starting Fake SSH Honeypot on port 2222"
python honeypot.py > ../honeypot.log 2>&1 &
HONEYPOT_PID=$!
echo "Honeypot started (PID: $HONEYPOT_PID)"
sleep 2

# Start Dashboard (Vite/React)
echo "Starting Live Dashboard → Opening in browser..."
cd ../dashboard
npm run dev > ../dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 3

# Open browser (Kali/Debian compatible)
xdg-open http://localhost:5173 2>/dev/null || true

# Final success message
echo ""
echo "=========================================="
echo "     ALL SYSTEMS RUNNING SUCCESSFULLY!     "
echo "=========================================="
echo "   Dashboard → http://localhost:5173"
echo "   API       → http://localhost:8000"
echo "   Honeypot  → Listening on port 2222"
echo ""
echo "Expose port 2222 to the internet → watch real attacks in minutes!"
echo ""
echo "Logs:"
echo "   API:        tail -f api.log"
echo "   Honeypot:   tail -f honeypot.log"
echo "   Dashboard:  tail -f dashboard.log"
echo ""
echo "To stop: Ctrl+C or run:"
echo "   kill $API_PID $HONEYPOT_PID $DASHBOARD_PID"
echo "=========================================="

# Keep script running so PIDs stay valid
wait
