#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install it with:"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.example to .env and configure it."
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3010}"
PID_DIR="$ROOT_DIR/.pids"
mkdir -p "$PID_DIR"

cleanup() {
  echo "Shutting down..."
  [[ -f "$PID_DIR/backend.pid" ]] && kill "$(cat "$PID_DIR/backend.pid")" 2>/dev/null || true
  [[ -f "$PID_DIR/frontend.pid" ]] && kill "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null || true
  rm -f "$PID_DIR/backend.pid" "$PID_DIR/frontend.pid"
}
trap cleanup EXIT INT TERM

echo "Starting backend on port ${BACKEND_PORT}..."
(
  cd "$ROOT_DIR/backend"
  uv run uvicorn app.main:app --host "${BACKEND_HOST:-127.0.0.1}" --port "$BACKEND_PORT" --reload
) &
echo $! > "$PID_DIR/backend.pid"

echo "Starting frontend on port ${FRONTEND_PORT}..."
(
  cd "$ROOT_DIR/frontend"
  npm run dev -- -p "$FRONTEND_PORT"
) &
echo $! > "$PID_DIR/frontend.pid"

echo ""
echo "ResumeAgent running:"
echo "  Frontend: http://localhost:${FRONTEND_PORT}"
echo "  Backend:  http://localhost:${BACKEND_PORT}"
echo "  API docs: http://localhost:${BACKEND_PORT}/docs"
echo ""
echo "Press Ctrl+C to stop."

wait
