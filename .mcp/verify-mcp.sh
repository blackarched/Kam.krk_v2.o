#!/bin/bash

###############################################################################
# MCP Server Verification Script
#
# Quickly verify that all MCP servers are properly installed and configured.
#
# Usage: bash .mcp/verify-mcp.sh
###############################################################################

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║           MCP Server Verification for CYBER-MATRIX              ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((pass++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((fail++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((warn++))
}

echo "Checking Prerequisites..."
echo "═══════════════════════════════════════════════════════════════════"

# Check Node.js
if command -v node &> /dev/null; then
    VERSION=$(node --version)
    check_pass "Node.js installed: $VERSION"
else
    check_fail "Node.js not found"
fi

# Check npm
if command -v npm &> /dev/null; then
    VERSION=$(npm --version)
    check_pass "npm installed: $VERSION"
else
    check_fail "npm not found"
fi

# Check Python
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version)
    check_pass "Python3 installed: $VERSION"
else
    check_warn "Python3 not found (Python server will not work)"
fi

# Check Git
if command -v git &> /dev/null; then
    VERSION=$(git --version)
    check_pass "Git installed: $VERSION"
else
    check_warn "Git not found (Git server will not work)"
fi

echo ""
echo "Checking MCP Server Installations..."
echo "═══════════════════════════════════════════════════════════════════"

# Check each MCP server
MCP_SERVERS=(
    "@modelcontextprotocol/server-filesystem"
    "@modelcontextprotocol/server-git"
    "@modelcontextprotocol/server-github"
    "@modelcontextprotocol/server-brave-search"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-sequential-thinking"
    "@modelcontextprotocol/server-sqlite"
)

for server in "${MCP_SERVERS[@]}"; do
    if npm list -g "$server" &> /dev/null; then
        VERSION=$(npm list -g "$server" 2>/dev/null | grep "$server" | awk '{print $2}' | sed 's/@//')
        check_pass "$server@$VERSION"
    else
        check_fail "$server not installed"
    fi
done

# Check Python MCP server
if command -v python3 &> /dev/null; then
    if pip3 show mcp-server-python &> /dev/null; then
        VERSION=$(pip3 show mcp-server-python 2>/dev/null | grep Version | awk '{print $2}')
        check_pass "mcp-server-python@$VERSION"
    else
        check_warn "mcp-server-python not installed"
    fi
fi

echo ""
echo "Checking Configuration Files..."
echo "═══════════════════════════════════════════════════════════════════"

# Check for config file
if [ -f ".mcp/mcp-config.json" ]; then
    check_pass "mcp-config.json exists"
else
    check_fail "mcp-config.json not found"
fi

# Check for .env.mcp
if [ -f ".env.mcp" ]; then
    check_pass ".env.mcp exists"
    
    # Check if tokens are set
    if grep -q "your_github_token_here" .env.mcp; then
        check_warn "GitHub token not configured in .env.mcp"
    else
        check_pass "GitHub token appears to be configured"
    fi
    
    if grep -q "your_brave_api_key_here" .env.mcp; then
        check_warn "Brave API key not configured in .env.mcp"
    else
        check_pass "Brave API key appears to be configured"
    fi
else
    check_warn ".env.mcp not found (optional for basic functionality)"
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q ".env.mcp" .gitignore; then
        check_pass ".env.mcp in .gitignore"
    else
        check_warn ".env.mcp not in .gitignore (security risk)"
    fi
    
    if grep -q ".mcp/memory" .gitignore; then
        check_pass ".mcp/memory in .gitignore"
    else
        check_warn ".mcp/memory not in .gitignore"
    fi
fi

echo ""
echo "Checking Directory Structure..."
echo "═══════════════════════════════════════════════════════════════════"

# Check directories
if [ -d ".mcp" ]; then
    check_pass ".mcp/ directory exists"
else
    check_fail ".mcp/ directory not found"
fi

if [ -d ".mcp/memory" ]; then
    check_pass ".mcp/memory/ directory exists"
else
    check_warn ".mcp/memory/ directory not found (will be auto-created)"
fi

# Check documentation files
DOCS=(
    ".mcp/README.md"
    ".mcp/setup-guide.md"
    ".mcp/test-mcp-servers.md"
    ".mcp/quick-reference.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        check_pass "$(basename $doc) exists"
    else
        check_warn "$(basename $doc) not found"
    fi
done

echo ""
echo "Checking IDE Configuration..."
echo "═══════════════════════════════════════════════════════════════════"

# Try to detect IDE config
if [[ "$OSTYPE" == "darwin"* ]]; then
    CURSOR_CONFIG="$HOME/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CURSOR_CONFIG="$HOME/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    CURSOR_CONFIG="$APPDATA/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
fi

if [ -f "$CURSOR_CONFIG" ]; then
    check_pass "IDE MCP configuration file found"
    
    # Check if it contains MCP servers
    if grep -q "mcpServers" "$CURSOR_CONFIG"; then
        check_pass "MCP servers configured in IDE"
    else
        check_warn "MCP servers not configured in IDE config file"
    fi
else
    check_warn "IDE MCP configuration file not found (may need manual setup)"
    echo "   Expected location: $CURSOR_CONFIG"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Verification Summary"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

echo -e "${GREEN}Passed:${NC} $pass"
echo -e "${YELLOW}Warnings:${NC} $warn"
echo -e "${RED}Failed:${NC} $fail"
echo ""

if [ $fail -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart your IDE (Cursor or VS Code)"
    echo "2. Open a chat and ask: 'List available MCP servers'"
    echo "3. Follow testing guide: .mcp/test-mcp-servers.md"
    exit 0
else
    echo -e "${RED}✗ Some checks failed.${NC}"
    echo ""
    echo "To fix issues:"
    echo "1. Run: bash .mcp/install-mcp-servers.sh"
    echo "2. Check: .mcp/setup-guide.md"
    echo "3. Verify configuration paths are correct"
    exit 1
fi
