# CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite

🚀 **A complete cyberpunk-themed penetration testing dashboard with real-time functionality**

![Version](https://img.shields.io/badge/version-8.0-purple)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)

## 🎯 Overview

CYBER-MATRIX v8.0 is a comprehensive penetration testing suite featuring a stunning 3D holographic dashboard. It combines powerful network security tools with an immersive cyberpunk interface, providing real-time monitoring, vulnerability assessment, and attack simulation capabilities.

## ✨ Features

### 🌟 Core Functionality
- **Network Discovery & Scanning** - Discover devices on local networks
- **Port Scanning** - Comprehensive port enumeration with service detection
- **Vulnerability Assessment** - Automated security vulnerability scanning
- **Real-time System Monitoring** - Live CPU, memory, and network metrics
- **Attack Simulation** - Hydra brute-force and Metasploit exploit integration
- **Interactive Console** - Command-line interface with live feedback

### 🎨 Interface Features
- **3D Holographic Design** - Immersive cyberpunk aesthetic with matrix effects
- **Live Data Visualization** - Real-time charts and graphs
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Interactive Elements** - Hover effects, animations, and visual feedback
- **Satellite Network Map** - 3D visualization of network topology

### 📊 Dashboard Components
- **Network Scanner** - IP range scanning with live results
- **Port Scanner** - Target-specific port enumeration
- **Vulnerability Scanner** - Security assessment tools
- **Attack Dashboard** - Hydra and Metasploit integration
- **System Monitor** - Real-time performance metrics
- **Security Metrics** - Threat level and vulnerability indices
- **Network Activity** - Traffic analysis and monitoring
- **Performance Metrics** - Response time and throughput tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Linux/Unix system (recommended)
- Root privileges (for full network functionality)

### One-Command Installation
```bash
# Download and run the installer
curl -fsSL https://raw.githubusercontent.com/your-repo/CYBER-MATRIX/main/auto-install.sh | sudo bash
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/CYBER-MATRIX.git
cd CYBER-MATRIX

# Make startup script executable
chmod +x start.sh

# Run the application
sudo ./start.sh
```

### Access the Dashboard
- **Local Access**: http://localhost:5000
- **Network Access**: http://your-ip:5000

## 🔧 Installation Details

### System Dependencies
The installer automatically handles these, but for manual setup:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install nmap hydra nikto aircrack-ng

# Python Dependencies
pip install -r requirements.txt
```

### Optional Tools
- **nmap** - Network discovery and port scanning
- **hydra** - Brute-force attack tool
- **nikto** - Web vulnerability scanner
- **metasploit** - Exploitation framework
- **aircrack-ng** - WiFi security testing

## 📡 API Endpoints

### System Metrics
- `GET /api/system/metrics` - Current system metrics
- `GET /api/system/metrics/history` - Historical metrics data

### Network Operations
- `POST /api/network/scan` - Initiate network scan
- `GET /api/network/devices` - Get discovered devices
- `POST /api/port/scan` - Perform port scan
- `POST /api/vulnerability/scan` - Run vulnerability assessment

### Attack Simulation
- `POST /api/attack/hydra` - Hydra brute-force attack
- `POST /api/attack/metasploit` - Metasploit exploit
- `POST /api/console/execute` - Execute console commands

### Chart Data
- `GET /api/charts/scan_results` - Scan results chart data
- `GET /api/charts/port_status` - Port status chart data
- `GET /api/charts/vulnerability` - Vulnerability radar chart
- `GET /api/charts/system_metrics` - System metrics timeline

## 🎮 Usage Guide

### Network Scanning
1. Select network interface (eth0, wlan0, etc.)
2. Enter IP range in CIDR notation (e.g., 192.168.1.0/24)
3. Click "INITIATE NETWORK SCAN"
4. View results in the scan results chart

### Port Scanning
1. Enter target IP address
2. Specify port range (e.g., 1-1000)
3. Click "INITIATE PORT SCAN"
4. Monitor open ports in the port status chart

### Vulnerability Assessment
1. Enter target IP address
2. Select scan intensity (LOW, MEDIUM, HIGH, AGGRESSIVE)
3. Click "INITIATE VULNERABILITY SCAN"
4. Review vulnerabilities in the radar chart

### Attack Simulation
1. **Hydra Attack**: Enter target IP and select protocol
2. **Metasploit**: Choose target and exploit type
3. Monitor attack progress in real-time
4. View results in the console output

## 🔒 Security Considerations

### ⚠️ Important Warnings
- **Only use on networks you own or have explicit permission to test**
- This tool is for educational and authorized testing purposes only
- Unauthorized network scanning and attacks are illegal
- Always follow responsible disclosure practices

### Security Features
- Input validation and sanitization
- Command injection protection
- Rate limiting on API endpoints
- Secure database operations
- Privilege separation for network operations

## 🛠️ Architecture

### Backend Components
- **Flask Web Server** - Main application server
- **SQLite Database** - Data storage and persistence
- **System Monitoring** - Real-time metrics collection
- **Network Tools Integration** - nmap, hydra, metasploit wrappers
- **API Layer** - RESTful endpoints for frontend communication

### Frontend Components
- **3D Matrix Background** - Animated cyberpunk effects
- **Chart.js Integration** - Interactive data visualizations
- **Real-time Updates** - WebSocket-like API polling
- **Responsive Design** - Mobile-friendly interface
- **Interactive Console** - Command execution interface

## 📊 Performance Metrics

### System Requirements
- **Minimum**: 2GB RAM, 1GB disk space
- **Recommended**: 4GB RAM, 2GB disk space
- **Network**: 100Mbps for optimal scanning performance

### Scalability
- Supports networks up to /16 (65,534 hosts)
- Concurrent scan limit: 50 targets
- Real-time updates: 5-second intervals
- Database: Unlimited scan history storage

## 🐛 Troubleshooting

### Common Issues

**"Permission denied" errors**
```bash
# Run with sudo for network operations
sudo ./start.sh
```

**"Command not found" for network tools**
```bash
# Install missing tools
sudo apt install nmap hydra nikto
```

**Port 5000 already in use**
```bash
# Kill existing processes
sudo lsof -ti:5000 | xargs kill -9
```

**Charts not loading**
- Check browser console for JavaScript errors
- Ensure API endpoints are responding
- Verify internet connection for CDN resources

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=1
python3 app.py
```

## 📚 Documentation & AI Assistant Rules

**👉 IMPORTANT: Before editing or generating code, see [`docs/AI_INSTRUCTIONS.md`](docs/AI_INSTRUCTIONS.md)**

All AI assistant actions must follow these documented rules. This ensures consistency, security, and quality across the project.

- **For AI Assistants:** Read `docs/AI_INSTRUCTIONS.md` before performing any task
- **For Developers:** See `docs/index.md` for complete documentation index
- **Quick Reference:** Module-specific docs in `docs/modules/` directory

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/your-repo/CYBER-MATRIX.git
cd CYBER-MATRIX
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Testing
```bash
# Run test suite
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Chart.js** - Data visualization library
- **Tailwind CSS** - Utility-first CSS framework
- **Flask** - Python web framework
- **Scapy** - Packet manipulation library
- **Nmap** - Network discovery tool
- **Hydra** - Brute-force attack tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/CYBER-MATRIX/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/CYBER-MATRIX/wiki)
- **Discord**: [Community Server](https://discord.gg/cyber-matrix)

## 🔮 Future Roadmap

- [ ] Web application vulnerability scanning
- [ ] Wireless network attack modules
- [ ] Report generation and export
- [ ] Multi-user collaboration features
- [ ] Cloud deployment options
- [ ] Mobile application companion
- [ ] AI-powered vulnerability analysis

---

**⚠️ Disclaimer**: This tool is for educational and authorized testing purposes only. Users are responsible for ensuring they have proper authorization before scanning or testing any networks or systems.

**Made with 💜 by the CYBER-MATRIX team**