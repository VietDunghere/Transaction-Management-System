#!/bin/bash
# Chạy demo_transactions.py liên tục trong background.
# Gọi từ restart_backend.sh hoặc thủ công.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/demo.pid"
LOG_FILE="$PROJECT_ROOT/logs/demo.log"

# ── Stop old instance ──────────────────────────────────────
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping old demo sender (PID $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

mkdir -p "$(dirname "$LOG_FILE")"

# ── Wait for backend to be ready ──────────────────────────
echo "Waiting for backend on :8000..."
for i in $(seq 1 20); do
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "Backend ready."
        break
    fi
    sleep 2
done

# ── Start demo sender (infinite loop, 0.3 req/s, 20% loans) ─
echo "Starting demo data sender..."
nohup python3 -u "$PROJECT_ROOT/demo_transactions.py" \
    --url http://localhost:8000/api/v1 \
    --username operator1 \
    --password Demo@1234 \
    --rate 0.3 \
    --loans 20 \
    --customer-query "cu" \
    --merchant-query "mc" \
    >> "$LOG_FILE" 2>&1 &

DEMO_PID=$!
echo $DEMO_PID > "$PID_FILE"
echo "Demo sender started (PID $DEMO_PID) — log: logs/demo.log"
