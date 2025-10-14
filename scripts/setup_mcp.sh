#!/usr/bin/env bash
set -euo pipefail

# Install Node.js if missing
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

# Install MCP servers
npm i -g @modelcontextprotocol/server-filesystem@latest @modelcontextprotocol/server-http@latest @modelcontextprotocol/server-git@latest

echo "MCP servers installed:"
server-filesystem --version || true
server-http --version || true
server-git --version || true
