#!/bin/sh
set -eu

uv run --package qooing-backend uvicorn app.main:app \
  --app-dir backend --host 127.0.0.1 --port 8000 >/tmp/qooing-uvicorn.log 2>&1 &
qooing_server_pid=$!
qooing_chat_output=$(mktemp)
trap 'kill "$qooing_server_pid" 2>/dev/null || true; rm -f "$qooing_chat_output"' EXIT

attempt=0
until curl -fsS http://127.0.0.1:8000/api/health >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 20 ]; then
    cat /tmp/qooing-uvicorn.log
    exit 1
  fi
  sleep 0.25
done

curl -fsS http://127.0.0.1:8000/api/health
curl -fsS http://127.0.0.1:8000/api/wiki
curl -fsSN -X POST http://127.0.0.1:8000/api/chat \
  -H 'content-type: application/json' \
  -d '{"prompt":"수면 질문","baby_info":{}}' >"$qooing_chat_output"
cat "$qooing_chat_output"
grep -q '^event: done$' "$qooing_chat_output"
if grep -q '^event: error$' "$qooing_chat_output"; then
  exit 1
fi
