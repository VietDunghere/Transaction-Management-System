#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/run.pid"
LOG_FILE="$PROJECT_ROOT/logs/backend.log"

mkdir -p "$(dirname "$LOG_FILE")"

# ── Wait for Oracle to be healthy ──────────────────────────
echo "Checking Oracle container (oracle-tms)..."
for i in $(seq 1 30); do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' oracle-tms 2>/dev/null || echo "not_found")
    if [ "$STATUS" = "healthy" ]; then
        echo "Oracle is healthy."
        break
    fi
    if [ "$STATUS" = "not_found" ]; then
        echo "oracle-tms container not found — starting via docker compose..."
        cd "$PROJECT_ROOT" && docker compose up -d oracle
    fi
    echo "  Waiting for Oracle... ($i/30) status=$STATUS"
    sleep 5
done

if [ "$STATUS" != "healthy" ]; then
    echo "ERROR: Oracle not healthy after 150s. Aborting."
    exit 1
fi

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

# ── Run Alembic migrations ─────────────────────────────────
echo "Running Alembic migrations..."
cd "$PROJECT_ROOT/backend"
alembic upgrade head
echo "Migrations done."

# ── Start backend ──────────────────────────────────────────
echo "Starting backend..."
cd "$PROJECT_ROOT"
nohup python run.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "Backend started (PID $(cat $PID_FILE))"
