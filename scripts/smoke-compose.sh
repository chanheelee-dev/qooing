#!/bin/sh
set -eu

qooing_chat_output=$(mktemp)
trap 'docker compose down >/dev/null 2>&1 || true; rm -f "$qooing_chat_output"' EXIT

docker compose up --build -d

attempt=0
until curl -fsS http://127.0.0.1:8080/api/health >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 60 ]; then
    docker compose ps
    docker compose logs
    exit 1
  fi
  sleep 0.5
done

curl -fsS http://127.0.0.1:8000/api/health
curl -fsS http://127.0.0.1:8080/api/wiki
curl -fsSN -X POST http://127.0.0.1:8080/api/chat \
  -H 'content-type: application/json' \
  -d '{"prompt":"수면 질문","baby_info":{}}' >"$qooing_chat_output"
cat "$qooing_chat_output"
grep -q '^event: done$' "$qooing_chat_output"
if grep -q '^event: error$' "$qooing_chat_output"; then
  exit 1
fi
