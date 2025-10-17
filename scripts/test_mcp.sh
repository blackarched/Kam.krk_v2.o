#!/usr/bin/env bash
set -euo pipefail

set -a && [ -f ./.env ] && . ./.env || true; set +a

BASE_URL="http://${CYBER_MATRIX_HOST:-127.0.0.1}:${CYBER_MATRIX_PORT:-5000}"
KEY_HEADER="X-API-Key: ${CYBER_MATRIX_API_KEY:-}"

echo "Checking MCP servers..."
server-filesystem --help >/dev/null 2>&1 && echo "filesystem OK" || echo "filesystem missing"
server-http --help >/dev/null 2>&1 && echo "http OK" || echo "http missing"
server-git --help >/dev/null 2>&1 && echo "git OK" || echo "git missing"

echo "Checking backend availability..."
curl -sS "$BASE_URL/" >/dev/null && echo "backend OK" || echo "backend not reachable"

if [ -n "${CYBER_MATRIX_API_KEY:-}" ]; then
  echo "Verifying API key..."
  curl -sS -H "$KEY_HEADER" "$BASE_URL/api/auth/verify" || true
else
  echo "No CYBER_MATRIX_API_KEY in env; skip auth verify"
fi

echo "Testing port scan endpoint (may return 400 for invalid inputs, which is OK)"
curl -sS -X POST -H "$KEY_HEADER" -H "Content-Type: application/json" \
  "$BASE_URL/api/port/scan" -d "{\"target_ip\":\"127.0.0.1\",\"port_range\":\"22,80,443\"}" || true
