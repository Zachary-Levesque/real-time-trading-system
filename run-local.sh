#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/.logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

mkdir -p "$LOG_DIR"

if [[ ! -x "$BACKEND_DIR/.venv/bin/python" ]]; then
  echo "Missing backend virtualenv at $BACKEND_DIR/.venv"
  echo "Create it first with:"
  echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Missing frontend dependencies in $FRONTEND_DIR/node_modules"
  echo "Install them first with:"
  echo "  cd frontend && npm install"
  exit 1
fi

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

(
  cd "$BACKEND_DIR"
  export STORAGE_MODE=file
  exec ./.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  exec npm run dev -- --host 0.0.0.0 --port 5173
) >"$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo "Starting Real-Time Trading System..."
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000/api/v1/health"
echo "Logs:"
echo "  $BACKEND_LOG"
echo "  $FRONTEND_LOG"
echo "Press Ctrl+C to stop both services."

wait "$BACKEND_PID" "$FRONTEND_PID"
