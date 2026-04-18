#!/usr/bin/env bash
set -e

BASE="http://127.0.0.1:8000"

echo "== health =="
curl -s "$BASE/health"
echo

echo "== ready =="
curl -s "$BASE/ready"
echo

echo "== telegram webhook =="
curl -s -X POST "$BASE/webhooks/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 10001,
    "message": {
      "message_id": 501,
      "text": "/builder inspect current run",
      "chat": { "id": 777 },
      "from": {
        "id": "openclaw",
        "username": "openclaw",
        "first_name": "OpenClaw"
      }
    }
  }'
echo

echo "== operator latest =="
curl -s "$BASE/operator/latest"
echo

echo "== operator session =="
curl -s "$BASE/operator/session"
echo

echo "== debug runtime shape =="
curl -s "$BASE/debug/runtime-shape"
echo

echo "== debug run sample =="
curl -s "$BASE/debug/run-sample"
echo
