#!/usr/bin/env bash
set -euo pipefail

# Start backend with secure defaults
cd "$(dirname "$0")"/..
if [ ! -f .env ]; then
  echo "Creating .env from template..."
  cp .env.template .env
fi

set -a && . ./.env && set +a

# Ensure Python deps
if ! python3 -c "import flask" >/dev/null 2>&1; then
  echo "Installing Python dependencies (user scope)..."
  pip3 install --user -r requirements.txt
fi

echo "Running security tests..."
python3 test_security.py || true

echo "Starting app on ${CYBER_MATRIX_HOST:-127.0.0.1}:${CYBER_MATRIX_PORT:-5000} ..."
python3 app.py
