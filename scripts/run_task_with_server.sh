#!/usr/bin/env bash
set -euo pipefail

TASK=${1:-tasks/task1.json}
PORT=${2:-8001}
TIMEOUT_SECONDS=${3:-20}
PY=${PY:-venv/bin/python}

# prefer venv python when available
if [ ! -x "$PY" ]; then
  if command -v python >/dev/null 2>&1; then
    PY=$(command -v python)
  fi
fi

if [ ! -f "$TASK" ]; then
  echo "Task file not found: $TASK" >&2
  exit 2
fi

LOG=uvicorn_test.log
TMP_TASK=$(mktemp --suffix=.json)

cleanup() {
  rc=$?
  if [ -f ".test_server.pid" ]; then
    pid=$(cat .test_server.pid)
    echo "Stopping server (pid=$pid)"
    kill "$pid" >/dev/null 2>&1 || true
    rm -f .test_server.pid
  fi
  [ -f "$TMP_TASK" ] && rm -f "$TMP_TASK"
  exit $rc
}
trap cleanup EXIT

echo "Starting uvicorn on port $PORT using interpreter $PY..."
nohup "$PY" -m uvicorn src.main:app --port "$PORT" >"$LOG" 2>&1 &
PID=$!
echo $PID > .test_server.pid

# wait for readiness
start_ts=$(date +%s)
while true; do
  if curl -sSf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    echo "Server is ready"
    break
  fi
  now_ts=$(date +%s)
  elapsed=$((now_ts - start_ts))
  if [ $elapsed -ge $TIMEOUT_SECONDS ]; then
    echo "Server did not start in time (waited ${elapsed}s). See $LOG" >&2
    exit 3
  fi
  sleep 0.5
done

# patch task with test api_url
PORT="$PORT" "$PY" - <<'PY'
import json, os, sys
src, dst = sys.argv[1], sys.argv[2]
port = os.environ.get("PORT")
with open(src, 'r', encoding='utf-8') as fh:
    t = json.load(fh)

t['api_url'] = f"http://127.0.0.1:{port}/llm/analyze_chapter"
with open(dst, 'w', encoding='utf-8') as fh:
    json.dump(t, fh, ensure_ascii=False, indent=2)
PY "$TASK" "$TMP_TASK"

# run the task
"$PY" scripts/generate.py "$TMP_TASK"
RC=$?

if [ $RC -eq 0 ]; then
  echo "Task completed successfully"
else
  echo "Task failed with exit code $RC"
fi

# cleanup will run via trap
exit $RC
