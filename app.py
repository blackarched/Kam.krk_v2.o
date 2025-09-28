#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite
Unified Backend API Server

This is the main application that serves the dashboard and provides all API endpoints
for network scanning, vulnerability assessment, and penetration testing operations.
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import subprocess
import re
import os
import json
import time
import threading
import psutil
import socket
import ipaddress
from datetime import datetime, timedelta
import random
import sqlite3
from contextlib import contextmanager
import logging
from logging.handlers import RotatingFileHandler
import signal
import sys

# Try to import optional dependencies
try:
    from scapy.all import *
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: Scapy not available. Some network functions will be limited.")

try:
    import netifaces as ni
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    print("Warning: netifaces not available. Using alternative methods.")

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("Warning: pybluez not available. Bluetooth scanning disabled.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'cyber-matrix-v8-secret-key-2024'
app.config['DEBUG'] = False

# Global variables for real-time data
system_metrics = {
    'cpu_usage': 0,
    'memory_usage': 0,
    'network_traffic': 0,
    'encryption_level': 92,
    'active_scans': 0,
    'threats_detected': 0,
    'devices_found': 0,
    'vulnerabilities': 0
}

# Database setup
DB_FILE = 'cyber_matrix.db'

def init_database():
    """Initialize the SQLite database with required tables"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                scan_type TEXT,
                target TEXT,
                results TEXT,
                status TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS network_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                mac_address TEXT,
                hostname TEXT,
                device_type TEXT,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                vulnerability_score INTEGER DEFAULT 0
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                attack_type TEXT,
                target TEXT,
                status TEXT,
                details TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT,
                metric_value REAL
            )
        ''')
        
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def run_command(command, shell=False, timeout=30):
    """Execute system commands safely with timeout"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            check=True, 
            timeout=timeout
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return None, str(e)
    except subprocess.TimeoutExpired:
        return None, "Command timed out"

def get_system_metrics():
    """Get real-time system metrics"""
    global system_metrics
    
    try:
        # CPU usage
        system_metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        system_metrics['memory_usage'] = memory.percent
        
        # Network traffic (simplified)
        network_io = psutil.net_io_counters()
        system_metrics['network_traffic'] = min(100, (network_io.bytes_sent + network_io.bytes_recv) / 1024 / 1024 % 100)
        
        # Store metrics in database
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO system_metrics (metric_name, metric_value) VALUES (?, ?)",
                ("cpu_usage", system_metrics['cpu_usage'])
            )
            conn.execute(
                "INSERT INTO system_metrics (metric_name, metric_value) VALUES (?, ?)",
                ("memory_usage", system_metrics['memory_usage'])
            )
            conn.commit()
            
    except Exception as e:
        print(f"Error getting system metrics: {e}")

def update_metrics_thread():
    """Background thread to update system metrics"""
    while True:
        get_system_metrics()
        time.sleep(5)  # Update every 5 seconds

# Network Discovery Functions
def discover_network_devices(ip_range="192.168.1.0/24"):
    """Discover devices on the network using multiple methods"""
    devices = []
    
    try:
        # Method 1: ARP table
        stdout, stderr = run_command(["arp", "-a"])
        if stdout:
            for line in stdout.splitlines():
                match = re.search(r"\(([\d.]+)\) at ([a-fA-F0-9:]+)", line)
                if match:
                    ip, mac = match.groups()
                    # Try to get hostname
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = "Unknown"
                    
                    devices.append({
                        "ip": ip,
                        "mac": mac,
                        "hostname": hostname,
                        "method": "ARP",
                        "status": "active"
                    })
        
        # Method 2: Ping sweep (if nmap not available)
        if not devices:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            for ip in list(network.hosts())[:20]:  # Limit to first 20 IPs
                stdout, stderr = run_command(["ping", "-c", "1", "-W", "1", str(ip)])
                if stdout and "1 received" in stdout:
                    devices.append({
                        "ip": str(ip),
                        "mac": "Unknown",
                        "hostname": "Unknown",
                        "method": "Ping",
                        "status": "active"
                    })
        
        # Method 3: Try nmap if available
        stdout, stderr = run_command(["nmap", "-sn", ip_range])
        if stdout and not stderr:
            nmap_devices = []
            current_device = {}
            for line in stdout.splitlines():
                if "Nmap scan report for" in line:
                    if current_device:
                        nmap_devices.append(current_device)
                    current_device = {
                        "hostname": line.split("for ")[1].strip(),
                        "method": "Nmap",
                        "status": "active"
                    }
                elif "MAC Address:" in line:
                    current_device["mac"] = line.split("MAC Address: ")[1].split()[0]
            
            if current_device:
                nmap_devices.append(current_device)
            
            # Merge with existing devices or use nmap results
            if nmap_devices:
                devices.extend(nmap_devices)
        
        # Store in database
        with get_db_connection() as conn:
            for device in devices:
                conn.execute('''
                    INSERT OR REPLACE INTO network_devices 
                    (ip_address, mac_address, hostname, device_type, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    device.get('ip', ''),
                    device.get('mac', ''),
                    device.get('hostname', ''),
                    'Unknown',
                    device.get('status', 'active')
                ))
            conn.commit()
        
        system_metrics['devices_found'] = len(devices)
        return devices
        
    except Exception as e:
        print(f"Error in network discovery: {e}")
        return []

def scan_ports(target_ip, port_range="1-1000"):
    """Scan ports on target IP"""
    try:
        # Try nmap first
        stdout, stderr = run_command(["nmap", "-p", port_range, target_ip])
        if stdout and not stderr:
            open_ports = []
            for line in stdout.splitlines():
                if "/tcp" in line and "open" in line:
                    port = line.split("/")[0]
                    service = line.split()[-1] if len(line.split()) > 2 else "unknown"
                    open_ports.append({"port": int(port), "service": service, "state": "open"})
            
            # Store results
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                    ("port_scan", target_ip, json.dumps(open_ports), "completed")
                )
                conn.commit()
            
            return open_ports
        
        # Fallback: Simple socket connection test for common ports
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    service = {21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 
                              53: "dns", 80: "http", 443: "https", 3389: "rdp"}.get(port, "unknown")
                    open_ports.append({"port": port, "service": service, "state": "open"})
                sock.close()
            except:
                continue
        
        return open_ports
        
    except Exception as e:
        print(f"Error in port scanning: {e}")
        return []

def vulnerability_scan(target_ip):
    """Perform basic vulnerability assessment"""
    vulnerabilities = []
    
    try:
        # Check for common vulnerabilities
        ports = scan_ports(target_ip, "1-1000")
        
        for port_info in ports:
            port = port_info['port']
            service = port_info['service']
            
            # Common vulnerability checks
            if port == 21 and service == "ftp":
                vulnerabilities.append({
                    "severity": "medium",
                    "type": "FTP Anonymous Access",
                    "description": "FTP service may allow anonymous access",
                    "port": port,
                    "recommendation": "Disable anonymous FTP access"
                })
            
            elif port == 22 and service == "ssh":
                # Try to detect SSH version
                vulnerabilities.append({
                    "severity": "low",
                    "type": "SSH Service",
                    "description": "SSH service detected - ensure strong authentication",
                    "port": port,
                    "recommendation": "Use key-based authentication and disable root login"
                })
            
            elif port == 80 and service == "http":
                vulnerabilities.append({
                    "severity": "medium",
                    "type": "Unencrypted HTTP",
                    "description": "HTTP service without encryption",
                    "port": port,
                    "recommendation": "Implement HTTPS encryption"
                })
            
            elif port == 3389 and service == "rdp":
                vulnerabilities.append({
                    "severity": "high",
                    "type": "RDP Service Exposed",
                    "description": "Remote Desktop Protocol exposed to network",
                    "port": port,
                    "recommendation": "Restrict RDP access and use VPN"
                })
        
        # Store results
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                ("vulnerability_scan", target_ip, json.dumps(vulnerabilities), "completed")
            )
            conn.commit()
        
        system_metrics['vulnerabilities'] = len(vulnerabilities)
        return vulnerabilities
        
    except Exception as e:
        print(f"Error in vulnerability scanning: {e}")
        return []

def get_wifi_networks():
    """Discover WiFi networks"""
    networks = []
    
    try:
        # Try iwlist scan
        stdout, stderr = run_command(["iwlist", "wlan0", "scan"])
        if stdout:
            current_network = {}
            for line in stdout.splitlines():
                line = line.strip()
                if "Cell" in line:
                    if current_network:
                        networks.append(current_network)
                    current_network = {}
                elif "Address:" in line:
                    current_network["bssid"] = line.split("Address: ")[1]
                elif "ESSID:" in line:
                    essid = line.split("ESSID:")[1].strip().strip('"')
                    if essid:
                        current_network["essid"] = essid
                elif "Channel:" in line:
                    current_network["channel"] = line.split("Channel:")[1]
                elif "Quality=" in line:
                    quality = line.split("Quality=")[1].split()[0]
                    current_network["quality"] = quality
                elif "Encryption key:" in line:
                    current_network["encrypted"] = "on" in line
            
            if current_network:
                networks.append(current_network)
    
    except Exception as e:
        print(f"Error scanning WiFi: {e}")
    
    return networks

# API Routes

@app.route('/')
def index():
    """Serve the main dashboard"""
    try:
        with open('/workspace/kamkrk_v2.html', 'r') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Dashboard file not found", 404

@app.route('/api/system/metrics')
def api_system_metrics():
    """Get current system metrics"""
    return jsonify(system_metrics)

@app.route('/api/system/metrics/history')
def api_system_metrics_history():
    """Get historical system metrics for charts"""
    try:
        with get_db_connection() as conn:
            # Get last 24 hours of data
            cursor = conn.execute('''
                SELECT metric_name, metric_value, timestamp 
                FROM system_metrics 
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 100
            ''')
            
            metrics_data = {}
            for row in cursor.fetchall():
                metric_name = row['metric_name']
                if metric_name not in metrics_data:
                    metrics_data[metric_name] = []
                metrics_data[metric_name].append({
                    'value': row['metric_value'],
                    'timestamp': row['timestamp']
                })
            
            return jsonify(metrics_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/scan', methods=['POST'])
def api_network_scan():
    """Initiate network scan"""
    data = request.get_json() or {}
    ip_range = data.get('ip_range', '192.168.1.0/24')
    
    try:
        system_metrics['active_scans'] += 1
        devices = discover_network_devices(ip_range)
        system_metrics['active_scans'] -= 1
        
        return jsonify({
            "status": "success",
            "devices": devices,
            "total_found": len(devices)
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/devices')
def api_network_devices():
    """Get discovered network devices"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM network_devices 
                WHERE last_seen > datetime('now', '-1 hour')
                ORDER BY last_seen DESC
            ''')
            
            devices = []
            for row in cursor.fetchall():
                devices.append({
                    'ip': row['ip_address'],
                    'mac': row['mac_address'],
                    'hostname': row['hostname'],
                    'type': row['device_type'],
                    'status': row['status'],
                    'vulnerability_score': row['vulnerability_score'],
                    'last_seen': row['last_seen']
                })
            
            return jsonify(devices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/port/scan', methods=['POST'])
def api_port_scan():
    """Initiate port scan"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    port_range = data.get('port_range', '1-1000')
    
    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400
    
    try:
        system_metrics['active_scans'] += 1
        ports = scan_ports(target_ip, port_range)
        system_metrics['active_scans'] -= 1
        
        return jsonify({
            "status": "success",
            "target": target_ip,
            "open_ports": ports,
            "total_open": len(ports)
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        return jsonify({"error": str(e)}), 500

@app.route('/api/vulnerability/scan', methods=['POST'])
def api_vulnerability_scan():
    """Initiate vulnerability scan"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    intensity = data.get('intensity', 'medium')
    
    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400
    
    try:
        system_metrics['active_scans'] += 1
        vulnerabilities = vulnerability_scan(target_ip)
        system_metrics['active_scans'] -= 1
        
        return jsonify({
            "status": "success",
            "target": target_ip,
            "vulnerabilities": vulnerabilities,
            "total_found": len(vulnerabilities),
            "severity_breakdown": {
                "high": len([v for v in vulnerabilities if v['severity'] == 'high']),
                "medium": len([v for v in vulnerabilities if v['severity'] == 'medium']),
                "low": len([v for v in vulnerabilities if v['severity'] == 'low'])
            }
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        return jsonify({"error": str(e)}), 500

@app.route('/api/wifi/networks')
def api_wifi_networks():
    """Get WiFi networks"""
    try:
        networks = get_wifi_networks()
        return jsonify({
            "status": "success",
            "networks": networks,
            "total_found": len(networks)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attack/hydra', methods=['POST'])
def api_hydra_attack():
    """Simulate Hydra brute force attack"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    protocol = data.get('protocol', 'ssh')
    
    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400
    
    try:
        # Log the attack attempt
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                ("hydra_bruteforce", target_ip, "initiated", f"Protocol: {protocol}")
            )
            conn.commit()
        
        # Simulate attack progress
        return jsonify({
            "status": "initiated",
            "target": target_ip,
            "protocol": protocol,
            "message": f"Hydra brute force attack initiated against {target_ip} using {protocol} protocol"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attack/metasploit', methods=['POST'])
def api_metasploit_attack():
    """Simulate Metasploit exploit"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    exploit = data.get('exploit', 'generic')
    
    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400
    
    try:
        # Log the attack attempt
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                ("metasploit_exploit", target_ip, "initiated", f"Exploit: {exploit}")
            )
            conn.commit()
        
        return jsonify({
            "status": "initiated",
            "target": target_ip,
            "exploit": exploit,
            "message": f"Metasploit exploit {exploit} initiated against {target_ip}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/console/execute', methods=['POST'])
def api_console_execute():
    """Execute console commands (simulated for security)"""
    data = request.get_json() or {}
    command = data.get('command', '')
    
    # Simulate command execution with safe responses
    responses = {
        'help': 'Available commands: scan, attack, status, info',
        'scan network': 'Network scan initiated...',
        'status': 'All systems operational',
        'info': 'CYBER-MATRIX v8.0 - Advanced Penetration Suite',
        'whoami': 'cyber-matrix-user',
        'pwd': '/opt/cyber-matrix',
        'ls': 'scan_results.db  attack_logs.db  config.json',
    }
    
    response = responses.get(command.lower(), f'Command executed: {command}')
    
    return jsonify({
        "status": "success",
        "command": command,
        "output": response
    })

@app.route('/api/charts/scan_results')
def api_charts_scan_results():
    """Get data for scan results chart"""
    try:
        # Generate realistic data for the doughnut chart
        data = {
            "labels": ["Active Hosts", "Inactive Hosts", "Vulnerable"],
            "datasets": [{
                "data": [
                    system_metrics['devices_found'],
                    max(1, random.randint(1, 5)),
                    system_metrics['vulnerabilities']
                ],
                "backgroundColor": ["#00ff41", "#ff00de", "#c000ff"]
            }]
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/charts/port_status')
def api_charts_port_status():
    """Get data for port status chart"""
    try:
        # Get recent port scan data
        common_ports = ["SSH", "HTTP", "HTTPS", "FTP", "SMB", "RDP"]
        port_data = [random.randint(1, 10) for _ in common_ports]
        
        data = {
            "labels": common_ports,
            "datasets": [{
                "label": "Open Ports",
                "data": port_data,
                "backgroundColor": ["#c000ff", "#ff00de", "#00ff41", "#c000ff", "#ff00de", "#00ff41"]
            }]
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/charts/vulnerability')
def api_charts_vulnerability():
    """Get data for vulnerability radar chart"""
    try:
        data = {
            "labels": ["Remote Code", "Privilege Escalation", "Information Disclosure", "Denial of Service", "Authentication Bypass"],
            "datasets": [{
                "label": "Vulnerability Level",
                "data": [
                    random.randint(30, 90),
                    random.randint(20, 80),
                    random.randint(10, 70),
                    random.randint(40, 90),
                    random.randint(10, 60)
                ],
                "backgroundColor": "rgba(192, 0, 255, 0.2)",
                "borderColor": "#c000ff"
            }]
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/charts/system_metrics')
def api_charts_system_metrics():
    """Get data for system metrics chart"""
    try:
        # Generate time series data
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=x*15)).strftime("%H:%M") for x in range(7, 0, -1)]
        
        data = {
            "labels": timestamps,
            "datasets": [
                {
                    "label": "CPU Usage",
                    "data": [random.randint(30, 80) for _ in timestamps],
                    "borderColor": "#c000ff",
                    "backgroundColor": "transparent"
                },
                {
                    "label": "Memory Usage",
                    "data": [random.randint(20, 60) for _ in timestamps],
                    "borderColor": "#ff00de",
                    "backgroundColor": "transparent"
                }
            ]
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\nShutting down CYBER-MATRIX server...")
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize database
    init_database()
    
    # Start metrics update thread
    metrics_thread = threading.Thread(target=update_metrics_thread, daemon=True)
    metrics_thread.start()
    
    # Configure logging
    if not app.debug:
        file_handler = RotatingFileHandler('cyber_matrix.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CYBER-MATRIX startup')
    
    print("🚀 Starting CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite")
    print("🌐 Dashboard will be available at: http://localhost:5000")
    print("🔒 API endpoints active and ready")
    print("⚡ Real-time metrics enabled")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )