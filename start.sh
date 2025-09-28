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

# Initialize database
echo -e "${BLUE}🗄️ Initializing database...${NC}"
python3 -c "
import sqlite3
import os

if os.path.exists('cyber_matrix.db'):
    os.remove('cyber_matrix.db')
    
conn = sqlite3.connect('cyber_matrix.db')
conn.execute('''CREATE TABLE IF NOT EXISTS scan_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    scan_type TEXT,
    target TEXT,
    results TEXT,
    status TEXT
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS network_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    mac_address TEXT,
    hostname TEXT,
    device_type TEXT,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    vulnerability_score INTEGER DEFAULT 0
)''')
conn.close()
print('Database initialized successfully')
"

# Get local IP for display
LOCAL_IP=$(python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "localhost")

echo ""
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎯 CYBER-MATRIX v8.0 READY TO LAUNCH! 🎯${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}🌐 ACCESS INFORMATION:${NC}"
echo -e "   ${BLUE}Local Access:${NC}    http://localhost:5000"
echo -e "   ${BLUE}Network Access:${NC}  http://$LOCAL_IP:5000"
echo -e "   ${BLUE}Dashboard:${NC}       Full holographic interface with live data"
echo ""
echo -e "${CYAN}🚀 FEATURES AVAILABLE:${NC}"
echo -e "   ${GREEN}✓${NC} Network Discovery & Scanning"
echo -e "   ${GREEN}✓${NC} Port Scanning & Service Detection"
echo -e "   ${GREEN}✓${NC} Vulnerability Assessment"
echo -e "   ${GREEN}✓${NC} Real-time System Monitoring"
echo -e "   ${GREEN}✓${NC} Interactive Attack Simulation"
echo -e "   ${GREEN}✓${NC} 3D Holographic Visualizations"
echo -e "   ${GREEN}✓${NC} Live Console Interface"
echo ""
echo -e "${YELLOW}⚠️ SECURITY REMINDER:${NC}"
echo -e "   Only use this tool on networks you own or have explicit permission to test"
echo ""
echo -e "${GREEN}🚀 Starting CYBER-MATRIX server...${NC}"
echo ""

# Start the application
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Shutting down CYBER-MATRIX...${NC}"; exit 0' INT

# Start the Flask application
python3 app.py