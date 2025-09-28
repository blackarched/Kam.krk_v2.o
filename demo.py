#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Demo Script
This script demonstrates the complete integration and functionality
"""

import time
import threading
import webbrowser
from app import app, init_database, system_metrics

def print_banner():
    print("\033[35m")
    print("""
 ██████╗██╗   ██╗██████╗ ███████╗██████╗       ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗      ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝█████╗██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════╝██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
╚██████╗   ██║   ██████╔╝███████╗██║  ██║      ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
    """)
    print("\033[0m")
    print("\033[36m🚀 CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite\033[0m")
    print("\033[33m⚡ Complete Integration Demo - Production Ready System\033[0m")
    print()

def demo_features():
    print("\033[32m✅ INTEGRATION COMPLETE - ALL FEATURES OPERATIONAL:\033[0m")
    print()
    
    features = [
        ("🌐 Unified Backend API", "15+ endpoints serving live data"),
        ("📊 Real-time Dashboard", "All charts display actual system metrics"),
        ("🔍 Network Discovery", "Live device scanning and enumeration"),
        ("🛡️ Security Assessment", "Vulnerability scanning with radar charts"),
        ("⚔️ Attack Simulation", "Hydra & Metasploit integration"),
        ("💻 Interactive Console", "Command execution with live feedback"),
        ("🎨 3D Visualizations", "Holographic satellite network maps"),
        ("📈 Performance Monitoring", "Real-time CPU, memory, network metrics"),
        ("🗄️ Data Persistence", "SQLite database with historical data"),
        ("🔒 Security Features", "Input validation and safe execution")
    ]
    
    for feature, description in features:
        print(f"   {feature:<25} {description}")
    
    print()

def show_api_endpoints():
    print("\033[34m🔗 ACTIVE API ENDPOINTS:\033[0m")
    endpoints = [
        ("GET  /api/system/metrics", "Current system performance"),
        ("POST /api/network/scan", "Network device discovery"),
        ("POST /api/port/scan", "Port enumeration"),
        ("POST /api/vulnerability/scan", "Security assessment"),
        ("POST /api/attack/hydra", "Brute force simulation"),
        ("POST /api/attack/metasploit", "Exploit simulation"),
        ("GET  /api/charts/*", "Live chart data (6 endpoints)"),
        ("POST /api/console/execute", "Command execution")
    ]
    
    for endpoint, description in endpoints:
        print(f"   {endpoint:<30} {description}")
    print()

def show_dashboard_components():
    print("\033[35m🎯 DASHBOARD COMPONENTS (All Functional):\033[0m")
    components = [
        ("Network Scanner", "Live IP range scanning with results"),
        ("Port Scanner", "Target-specific port enumeration"),
        ("Vulnerability Scanner", "Security assessment with radar chart"),
        ("Attack Dashboard", "Hydra/Metasploit with progress tracking"),
        ("System Monitor", "Real-time performance metrics"),
        ("Security Metrics", "Threat levels and indices"),
        ("Network Activity", "Traffic analysis and monitoring"),
        ("3D Satellite Map", "Network topology visualization"),
        ("Console Interface", "Interactive command execution")
    ]
    
    for component, description in components:
        print(f"   {component:<20} {description}")
    print()

def launch_demo():
    print_banner()
    demo_features()
    show_api_endpoints()
    show_dashboard_components()
    
    print("\033[33m⚡ STARTING CYBER-MATRIX SERVER...\033[0m")
    print()
    print("\033[32m🌐 Dashboard Access:\033[0m")
    print("   Local:    http://localhost:5000")
    print("   Network:  http://your-ip:5000")
    print()
    print("\033[36m🎮 DEMO INSTRUCTIONS:\033[0m")
    print("   1. Open the dashboard in your browser")
    print("   2. Try network scanning with IP range 192.168.1.0/24")
    print("   3. Test port scanning on a target IP")
    print("   4. Run vulnerability assessment")
    print("   5. Watch real-time metrics update")
    print("   6. Use the interactive console")
    print()
    print("\033[31m⚠️ SECURITY REMINDER:\033[0m")
    print("   Only scan networks you own or have permission to test")
    print()
    print("\033[33m🚀 Press Ctrl+C to stop the server\033[0m")
    print("=" * 80)
    
    # Initialize database
    init_database()
    
    # Try to open browser after a delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
        except:
            pass
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    launch_demo()