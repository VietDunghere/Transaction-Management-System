#!/bin/bash
set -e

PID_FILE="$(dirname "$0")/../run.pid"
LOG_FILE="$(dirname "$0")/../logs/backend.log"

mkdir -p "$(dirname "$LOG_FILE")"

# Kill process cũ nếu còn chạy
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

# Start process mới
echo "Starting backend..."
nohup python run.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "Backend started (PID $(cat $PID_FILE))"
