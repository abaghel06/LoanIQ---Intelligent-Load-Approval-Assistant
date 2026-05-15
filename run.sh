#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
  exit 1
fi

cleanup() {
  echo ""
  echo "Shutting down..."
  kill "$FASTAPI_PID" 2>/dev/null
  wait "$FASTAPI_PID" 2>/dev/null
}
trap cleanup EXIT INT TERM

echo "Starting FastAPI on http://localhost:8000 ..."
uvicorn api.main:app --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to be ready
for i in $(seq 1 20); do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "FastAPI is ready."
    break
  fi
  sleep 0.5
done

echo "Starting Streamlit on http://localhost:8501 ..."
streamlit run ui/app.py
