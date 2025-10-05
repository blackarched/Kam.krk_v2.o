#!/bin/bash

# CYBER-MATRIX v8.0 - Fixed Startup Script
# Handles dependency installation and proper startup

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "🚀 CYBER-MATRIX v8.0 - Fixed Startup"
echo "=================================="
echo -e "${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip to fix CVE-2025-8869
echo -e "${BLUE}🔒 Upgrading pip for security...${NC}"
pip install --upgrade pip>=25.2

# Install core dependencies
echo -e "${BLUE}📦 Installing core dependencies...${NC}"
pip install flask>=3.0.0 flask-cors>=4.0.0 psutil>=5.9.0

# Install additional dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦 Installing additional dependencies...${NC}"
    pip install -r requirements.txt || echo -e "${YELLOW}⚠️ Some optional dependencies failed to install${NC}"
fi

# Generate API key if not set
if [ -z "${CYBER_MATRIX_API_KEY}" ]; then
    export CYBER_MATRIX_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo -e "${GREEN}🔑 Generated API Key: $CYBER_MATRIX_API_KEY${NC}"
fi

# Test imports
echo -e "${BLUE}🧪 Testing imports...${NC}"
python3 -c "
import flask, flask_cors, psutil
print('✅ Core imports successful')
"

echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo -e "${BLUE}🌐 Starting CYBER-MATRIX...${NC}"
echo -e "${YELLOW}📝 Access at: http://127.0.0.1:5000${NC}"
echo -e "${YELLOW}🔑 API Key: $CYBER_MATRIX_API_KEY${NC}"
echo ""

# Start the application
python3 app.py