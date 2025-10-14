#!/bin/bash

###############################################################################
# MCP Server Installation Script for CYBER-MATRIX v8.0
#
# This script installs and configures all MCP servers needed for development
# in Cursor or VS Code.
#
# Usage: bash .mcp/install-mcp-servers.sh
###############################################################################

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║       MCP Server Installation for CYBER-MATRIX v8.0             ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
echo "═══════════════════════════════════════════════════════════════════"
echo "1. Checking Prerequisites"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
    
    # Check if version is 18+
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -lt 18 ]; then
        print_error "Node.js version must be 18 or higher. Current: $NODE_VERSION"
        exit 1
    fi
else
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm is not installed."
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_warning "Python3 is not installed. Python MCP server will be skipped."
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    print_success "pip3 installed: $PIP_VERSION"
else
    print_warning "pip3 is not installed. Python MCP server will be skipped."
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_success "Git installed: $GIT_VERSION"
else
    print_warning "Git is not installed. Git MCP server will have limited functionality."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "2. Installing MCP Servers"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Install Node.js-based MCP servers
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
    print_info "Installing $server..."
    if npm install -g "$server" &> /dev/null; then
        print_success "Installed $server"
    else
        print_error "Failed to install $server"
    fi
done

# Install Python MCP server if Python is available
if command -v python3 &> /dev/null && command -v pip3 &> /dev/null; then
    echo ""
    print_info "Installing Python MCP server..."
    if pip3 install mcp-server-python &> /dev/null; then
        print_success "Installed mcp-server-python"
    else
        print_warning "Failed to install mcp-server-python. You may need to install it manually."
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "3. Creating Configuration Files"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Create .mcp directory if it doesn't exist
mkdir -p .mcp/memory

# Create .gitignore entry for MCP
if [ -f .gitignore ]; then
    if ! grep -q ".mcp/memory" .gitignore; then
        echo "" >> .gitignore
        echo "# MCP server data" >> .gitignore
        echo ".mcp/memory/" >> .gitignore
        echo ".env.mcp" >> .gitignore
        print_success "Added MCP entries to .gitignore"
    else
        print_info ".gitignore already contains MCP entries"
    fi
fi

# Create template .env.mcp file
if [ ! -f .env.mcp ]; then
    cat > .env.mcp << 'EOF'
# MCP Server Environment Variables
# DO NOT COMMIT THIS FILE - IT CONTAINS SECRETS

# GitHub Personal Access Token (optional but recommended)
# Get it from: https://github.com/settings/tokens
# Required scopes: repo, read:org, read:user
GITHUB_TOKEN=your_github_token_here

# Brave Search API Key (optional)
# Get it from: https://brave.com/search/api/
BRAVE_API_KEY=your_brave_api_key_here

# Python path (usually auto-detected)
PYTHON_PATH=/usr/bin/python3

# Workspace root (usually auto-detected)
WORKSPACE_ROOT=/workspace
EOF
    print_success "Created .env.mcp template"
    print_warning "Please edit .env.mcp and add your API tokens"
else
    print_info ".env.mcp already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "4. Detecting Configuration Paths"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Detect OS and IDE configuration path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CURSOR_CONFIG="$HOME/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    VSCODE_CONFIG="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    print_info "Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CURSOR_CONFIG="$HOME/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    VSCODE_CONFIG="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    print_info "Detected Linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    CURSOR_CONFIG="$APPDATA/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    VSCODE_CONFIG="$APPDATA/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    print_info "Detected Windows"
else
    print_warning "Unknown OS type: $OSTYPE"
fi

# Find npx path
NPX_PATH=$(which npx)
print_info "npx path: $NPX_PATH"

# Find python3 path
if command -v python3 &> /dev/null; then
    PYTHON3_PATH=$(which python3)
    print_info "python3 path: $PYTHON3_PATH"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "5. Configuration Instructions"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

print_info "MCP servers have been installed!"
echo ""
print_warning "NEXT STEPS:"
echo ""
echo "1. Copy the MCP configuration to your IDE:"
echo ""
if [ -f "$CURSOR_CONFIG" ]; then
    print_success "Cursor configuration detected at:"
    echo "   $CURSOR_CONFIG"
    echo ""
    echo "   Copy .mcp/mcp-config.json to this location"
elif [ -f "$VSCODE_CONFIG" ]; then
    print_success "VS Code configuration detected at:"
    echo "   $VSCODE_CONFIG"
    echo ""
    echo "   Copy .mcp/mcp-config.json to this location"
else
    print_info "No IDE configuration found. You may need to:"
    echo "   - Install Cursor or VS Code"
    echo "   - Install the Claude Dev or Cline extension"
    echo "   - Then copy .mcp/mcp-config.json to the config location"
fi

echo ""
echo "2. Update paths in the configuration:"
echo "   - Replace 'npx' with: $NPX_PATH"
if command -v python3 &> /dev/null; then
    echo "   - Replace 'python3' with: $PYTHON3_PATH"
fi
echo "   - Replace '/workspace' with: $(pwd)"
echo ""

echo "3. Add your API tokens to .env.mcp:"
echo "   - GitHub token (optional but recommended)"
echo "   - Brave Search API key (optional)"
echo ""

echo "4. Restart your IDE (Cursor or VS Code)"
echo ""

echo "5. Verify MCP servers by asking your AI assistant:"
echo "   'List available MCP servers and tools'"
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo "Installation Summary"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Count installed servers
INSTALLED_COUNT=0
for server in "${MCP_SERVERS[@]}"; do
    if npm list -g "$server" &> /dev/null; then
        ((INSTALLED_COUNT++))
    fi
done

print_success "Installed $INSTALLED_COUNT out of ${#MCP_SERVERS[@]} Node.js MCP servers"

if command -v python3 &> /dev/null && pip3 show mcp-server-python &> /dev/null; then
    print_success "Python MCP server installed"
fi

echo ""
print_success "Installation complete!"
echo ""
print_info "For detailed setup instructions, see: .mcp/setup-guide.md"
echo ""
