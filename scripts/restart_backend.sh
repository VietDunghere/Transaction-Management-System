#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/run.pid"
LOG_FILE="$PROJECT_ROOT/logs/backend.log"

mkdir -p "$(dirname "$LOG_FILE")"

# ── Kill old backend process ───────────────────────────────
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping old process (PID $OLD_PID)..."
        kill "$OLD_PID"
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# Fallback: kill theo port 8000 nếu PID file không còn chính xác
STALE=$(lsof -t -i:8000 2>/dev/null || true)
if [ -n "$STALE" ]; then
    echo "Killing stale process on port 8000..."
    kill "$STALE" 2>/dev/null || true
    sleep 1
fi

# ── Init DB (idempotent: create tables + seed) ─────────────
echo "Running init_db..."
python "$PROJECT_ROOT/scripts/init_db.py"
echo "init_db done."

# ── Start backend ──────────────────────────────────────────
echo "Starting backend..."
cd "$PROJECT_ROOT"
nohup python run.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "Backend started (PID $(cat $PID_FILE))"
