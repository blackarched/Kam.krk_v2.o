#!/bin/bash

# CYBER-MATRIX v8.0 Startup Script
# This script sets up and starts the complete penetration testing suite

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}"
cat << "EOF"
 ██████╗██╗   ██╗██████╗ ███████╗██████╗       ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗      ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝█████╗██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════╝██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
╚██████╗   ██║   ██████╔╝███████╗██║  ██║      ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
EOF
echo -e "${NC}"

echo -e "${CYAN}🚀 CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite${NC}"
echo -e "${YELLOW}⚡ Starting complete cyberpunk dashboard with live functionality${NC}"
echo ""

# Check if running as root for network operations
if [[ $EUID -eq 0 ]]; then
    echo -e "${GREEN}✓ Running with root privileges - all network functions available${NC}"
else
    echo -e "${YELLOW}⚠ Running without root - some network functions may be limited${NC}"
    echo -e "${YELLOW}  For full functionality, run: sudo ./start.sh${NC}"
fi

# Check Python installation
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.7+${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Check for optional system tools
echo -e "${BLUE}🔍 Checking system tools availability...${NC}"

tools_available=0
total_tools=5

if command -v nmap &> /dev/null; then
    echo -e "${GREEN}✓ nmap available${NC}"
    tools_available=$((tools_available + 1))
else
    echo -e "${YELLOW}⚠ nmap not found (install with: sudo apt install nmap)${NC}"
fi

if command -v hydra &> /dev/null; then
    echo -e "${GREEN}✓ hydra available${NC}"
    tools_available=$((tools_available + 1))
else
    echo -e "${YELLOW}⚠ hydra not found (install with: sudo apt install hydra)${NC}"
fi

if command -v nikto &> /dev/null; then
    echo -e "${GREEN}✓ nikto available${NC}"
    tools_available=$((tools_available + 1))
else
    echo -e "${YELLOW}⚠ nikto not found (install with: sudo apt install nikto)${NC}"
fi

if command -v msfconsole &> /dev/null; then
    echo -e "${GREEN}✓ metasploit available${NC}"
    tools_available=$((tools_available + 1))
else
    echo -e "${YELLOW}⚠ metasploit not found${NC}"
fi

if command -v aircrack-ng &> /dev/null; then
    echo -e "${GREEN}✓ aircrack-ng suite available${NC}"
    tools_available=$((tools_available + 1))
else
    echo -e "${YELLOW}⚠ aircrack-ng not found (install with: sudo apt install aircrack-ng)${NC}"
fi

echo -e "${BLUE}📊 Tool availability: $tools_available/$total_tools${NC}"

# Start the application
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Shutting down CYBER-MATRIX...${NC}"; exit 0' INT

# Start the Flask application
python3 app.py