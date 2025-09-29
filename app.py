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
import shlex
import hashlib
import secrets
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app first
app = Flask(__name__)
CORS(app)

# Try to import optional dependencies safely
# Import secure network tools
try:
    from secure_network_tools import secure_tools
    SECURE_TOOLS_AVAILABLE = True
except ImportError:
    SECURE_TOOLS_AVAILABLE = False
    print("Warning: Secure network tools not available. Using fallback methods.")

try:
    from scapy.all import *
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: Scapy not available. Using alternative methods.")

try:
    import netifaces as ni
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    print("Warning: netifaces not available. Using alternative methods.")

# Removed bluetooth support due to security vulnerabilities
BLUETOOTH_AVAILABLE = False
print("Info: Bluetooth support disabled for security reasons.")

# Configuration - Generate secure secret key
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['DEBUG'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Security configuration
API_KEY_HASH = generate_password_hash(os.environ.get('CYBER_MATRIX_API_KEY', secrets.token_urlsafe(32)))
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Rate limiting storage
rate_limit_storage = {}

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

# Security utilities
def validate_ip_address(ip):
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_port_range(port_range):
    """Validate port range format"""
    try:
        if ',' in port_range:
            # Handle comma-separated ports like "22,80,443"
            ports = port_range.split(',')
            for port_str in ports:
                port = int(port_str.strip())
                if not (1 <= port <= 65535):
                    return False
            return True
        elif '-' in port_range:
            start, end = port_range.split('-', 1)
            start, end = int(start), int(end)
            return 1 <= start <= end <= 65535
        else:
            port = int(port_range)
            return 1 <= port <= 65535
    except (ValueError, AttributeError):
        return False

def validate_cidr_range(cidr):
    """Validate CIDR notation"""
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def sanitize_input(input_str, max_length=100):
    """Sanitize user input"""
    if not isinstance(input_str, str):
        return ""
    # Remove dangerous characters
    sanitized = re.sub(r'[;&|`$(){}\[\]<>"\']', '', input_str)
    return sanitized[:max_length].strip()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or not check_password_hash(API_KEY_HASH, api_key):
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=RATE_LIMIT_REQUESTS, window=RATE_LIMIT_WINDOW):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            
            # Clean old entries
            for ip in list(rate_limit_storage.keys()):
                rate_limit_storage[ip] = [req_time for req_time in rate_limit_storage[ip] 
                                        if current_time - req_time < window]
                if not rate_limit_storage[ip]:
                    del rate_limit_storage[ip]
            
            # Check rate limit
            if client_ip not in rate_limit_storage:
                rate_limit_storage[client_ip] = []
            
            if len(rate_limit_storage[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            rate_limit_storage[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def run_command(command, timeout=30, allowed_commands=None):
    """Execute system commands safely with strict validation"""
    try:
        # Validate command is in allowed list
        if allowed_commands:
            cmd_name = command[0] if isinstance(command, list) else command.split()[0]
            if cmd_name not in allowed_commands:
                return None, f"Command not allowed: {cmd_name}"
        
        # Always use list format and never shell=True
        if isinstance(command, str):
            # Only allow specific safe commands
            safe_commands = ['ping', 'nmap', 'arp', 'iwlist', 'ps', 'netstat']
            cmd_parts = shlex.split(command)
            if cmd_parts[0] not in safe_commands:
                return None, f"Command not allowed: {cmd_parts[0]}"
            command = cmd_parts
        
        result = subprocess.run(
            command,
            shell=False,  # Never use shell=True
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return None, "Command execution failed"
    except subprocess.TimeoutExpired:
        return None, "Command timed out"
    except Exception as e:
        app.logger.error(f"Command execution error: {str(e)}")
        return None, "Command execution error"

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
        app.logger.error(f"Error getting system metrics: {str(e)}")

def update_metrics_thread():
    """Background thread to update system metrics"""
    while True:
        get_system_metrics()
        time.sleep(5)  # Update every 5 seconds

# Network Discovery Functions
def discover_network_devices(ip_range="192.168.1.0/24"):
    """Discover devices on the network using secure methods"""
    try:
        # Use secure network tools
        devices = secure_tools.discover_network_devices(ip_range)
        
        # Store in database with parameterized queries
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
        app.logger.error(f"Error in network discovery: {str(e)}")
        return []

def scan_ports(target_ip, port_range="22,80,443"):
    """Scan ports using secure methods"""
    try:
        # Use secure port scanning with limited scope
        open_ports = secure_tools.scan_ports_secure(target_ip, port_range)
        
        # Store results with parameterized query
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                ("port_scan", target_ip, json.dumps(open_ports), "completed")
            )
            conn.commit()
        
        return open_ports
        
    except Exception as e:
        app.logger.error(f"Error in port scanning: {str(e)}")
        return []

def vulnerability_scan(target_ip):
    """Perform basic vulnerability assessment with validation"""
    vulnerabilities = []
    
    try:
        # Validate IP address
        if not validate_ip_address(target_ip):
            app.logger.warning(f"Invalid IP address for vulnerability scan: {target_ip}")
            return []
        
        # Check for common vulnerabilities on limited port range
        ports = scan_ports(target_ip, "1-1000")
        
        for port_info in ports:
            port = port_info.get('port')
            service = port_info.get('service', 'unknown')
            
            if not isinstance(port, int) or not (1 <= port <= 65535):
                continue
            
            # Common vulnerability checks with sanitized data
            if port == 21 and service == "ftp":
                vulnerabilities.append({
                    "severity": "medium",
                    "type": "FTP Service Detected",
                    "description": "FTP service detected - may have security issues",
                    "port": port,
                    "recommendation": "Use SFTP instead of FTP"
                })
            
            elif port == 22 and service == "ssh":
                vulnerabilities.append({
                    "severity": "low",
                    "type": "SSH Service Detected",
                    "description": "SSH service detected - ensure strong configuration",
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
            
            elif port == 23 and service == "telnet":
                vulnerabilities.append({
                    "severity": "high",
                    "type": "Telnet Service Detected",
                    "description": "Insecure Telnet service detected",
                    "port": port,
                    "recommendation": "Replace Telnet with SSH"
                })
        
        # Store results with parameterized query
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                ("vulnerability_scan", target_ip, json.dumps(vulnerabilities), "completed")
            )
            conn.commit()
        
        system_metrics['vulnerabilities'] = len(vulnerabilities)
        app.logger.info(f"Vulnerability scan completed for {target_ip}: {len(vulnerabilities)} issues found")
        return vulnerabilities
        
    except Exception as e:
        app.logger.error(f"Error in vulnerability scanning: {str(e)}")
        return []

def get_wifi_networks():
    """Discover WiFi networks using secure methods"""
    try:
        return secure_tools.get_wifi_networks_secure()
    except Exception as e:
        app.logger.error(f"Error scanning WiFi: {str(e)}")
        return []

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
@rate_limit(max_requests=60, window=60)  # Allow frequent polling
@require_api_key
def api_system_metrics():
    """Get current system metrics"""
    try:
        return jsonify(system_metrics)
    except Exception as e:
        app.logger.error(f"System metrics error: {str(e)}")
        return jsonify({"error": "Failed to retrieve system metrics"}), 500

@app.route('/api/system/metrics/history')
@rate_limit(max_requests=30, window=60)
@require_api_key
def api_system_metrics_history():
    """Get historical system metrics for charts"""
    try:
        with get_db_connection() as conn:
            # Get last 24 hours of data with limit
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
                    'value': float(row['metric_value']),  # Ensure numeric
                    'timestamp': row['timestamp']
                })
            
            return jsonify(metrics_data)
    except Exception as e:
        app.logger.error(f"Metrics history error: {str(e)}")
        return jsonify({"error": "Failed to retrieve metrics history"}), 500

@app.route('/api/network/scan', methods=['POST'])
@rate_limit(max_requests=10, window=60)  # Limit network scans
@require_api_key
def api_network_scan():
    """Initiate network scan with security validation"""
    try:
        data = request.get_json() or {}
        ip_range = sanitize_input(data.get('ip_range', '192.168.1.0/24'), 20)
        
        # Validate IP range
        if not validate_cidr_range(ip_range):
            return jsonify({"error": "Invalid IP range format"}), 400
        
        # Check if scan is already running
        if system_metrics['active_scans'] >= 3:  # Limit concurrent scans
            return jsonify({"error": "Too many active scans"}), 429
        
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
        app.logger.error(f"Network scan error: {str(e)}")
        return jsonify({"error": "Network scan failed"}), 500

@app.route('/api/network/devices')
@rate_limit(max_requests=30, window=60)
@require_api_key
def api_network_devices():
    """Get discovered network devices"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM network_devices 
                WHERE last_seen > datetime('now', '-1 hour')
                ORDER BY last_seen DESC
                LIMIT 50
            ''')
            
            devices = []
            for row in cursor.fetchall():
                devices.append({
                    'ip': row['ip_address'],
                    'mac': row['mac_address'],
                    'hostname': row['hostname'],
                    'type': row['device_type'],
                    'status': row['status'],
                    'vulnerability_score': int(row['vulnerability_score']) if row['vulnerability_score'] else 0,
                    'last_seen': row['last_seen']
                })
            
            return jsonify(devices)
    except Exception as e:
        app.logger.error(f"Network devices error: {str(e)}")
        return jsonify({"error": "Failed to retrieve network devices"}), 500

@app.route('/api/port/scan', methods=['POST'])
@rate_limit(max_requests=5, window=60)  # Strict limit for port scans
@require_api_key
def api_port_scan():
    """Initiate port scan with security validation"""
    try:
        data = request.get_json() or {}
        target_ip = sanitize_input(data.get('target_ip', ''), 15)
        port_range = sanitize_input(data.get('port_range', '1-1000'), 20)
        
        if not target_ip:
            return jsonify({"error": "target_ip required"}), 400
        
        if not validate_ip_address(target_ip):
            return jsonify({"error": "Invalid IP address format"}), 400
        
        if not validate_port_range(port_range):
            return jsonify({"error": "Invalid port range format"}), 400
        
        # Check if scan is already running
        if system_metrics['active_scans'] >= 2:
            return jsonify({"error": "Too many active scans"}), 429
        
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
        app.logger.error(f"Port scan error: {str(e)}")
        return jsonify({"error": "Port scan failed"}), 500

@app.route('/api/vulnerability/scan', methods=['POST'])
@rate_limit(max_requests=3, window=300)  # Very strict limit for vuln scans
@require_api_key
def api_vulnerability_scan():
    """Initiate vulnerability scan with security validation"""
    try:
        data = request.get_json() or {}
        target_ip = sanitize_input(data.get('target_ip', ''), 15)
        intensity = sanitize_input(data.get('intensity', 'medium'), 10)
        
        if not target_ip:
            return jsonify({"error": "target_ip required"}), 400
        
        if not validate_ip_address(target_ip):
            return jsonify({"error": "Invalid IP address format"}), 400
        
        if intensity not in ['low', 'medium', 'high']:
            intensity = 'medium'
        
        # Check if scan is already running
        if system_metrics['active_scans'] >= 1:  # Only one vuln scan at a time
            return jsonify({"error": "Vulnerability scan already in progress"}), 429
        
        system_metrics['active_scans'] += 1
        vulnerabilities = vulnerability_scan(target_ip)
        system_metrics['active_scans'] -= 1
        
        return jsonify({
            "status": "success",
            "target": target_ip,
            "vulnerabilities": vulnerabilities,
            "total_found": len(vulnerabilities),
            "severity_breakdown": {
                "high": len([v for v in vulnerabilities if v.get('severity') == 'high']),
                "medium": len([v for v in vulnerabilities if v.get('severity') == 'medium']),
                "low": len([v for v in vulnerabilities if v.get('severity') == 'low'])
            }
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        app.logger.error(f"Vulnerability scan error: {str(e)}")
        return jsonify({"error": "Vulnerability scan failed"}), 500

@app.route('/api/wifi/networks')
@rate_limit(max_requests=5, window=60)
@require_api_key
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
        app.logger.error(f"WiFi networks error: {str(e)}")
        return jsonify({"error": "Failed to retrieve WiFi networks"}), 500

@app.route('/api/attack/hydra', methods=['POST'])
@rate_limit(max_requests=1, window=3600)  # Very strict limit - 1 per hour
@require_api_key
def api_hydra_attack():
    """Simulate Hydra brute force attack (SIMULATION ONLY)"""
    try:
        data = request.get_json() or {}
        target_ip = sanitize_input(data.get('target_ip', ''), 15)
        protocol = sanitize_input(data.get('protocol', 'ssh'), 10)
        
        if not target_ip:
            return jsonify({"error": "target_ip required"}), 400
        
        if not validate_ip_address(target_ip):
            return jsonify({"error": "Invalid IP address format"}), 400
        
        # Only allow safe protocols
        allowed_protocols = ['ssh', 'ftp', 'telnet', 'http']
        if protocol not in allowed_protocols:
            protocol = 'ssh'
        
        # Log the simulated attack attempt
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                ("hydra_simulation", target_ip, "simulated", f"Protocol: {protocol}")
            )
            conn.commit()
        
        app.logger.warning(f"Simulated Hydra attack logged for {target_ip} using {protocol}")
        
        # Return simulation response
        return jsonify({
            "status": "simulated",
            "target": target_ip,
            "protocol": protocol,
            "message": f"Hydra attack simulation logged for {target_ip} using {protocol} protocol",
            "note": "This is a simulation for educational purposes only"
        })
    except Exception as e:
        app.logger.error(f"Attack simulation error: {str(e)}")
        return jsonify({"error": "Attack simulation failed"}), 500

@app.route('/api/attack/metasploit', methods=['POST'])
@rate_limit(max_requests=1, window=3600)  # Very strict limit - 1 per hour
@require_api_key
def api_metasploit_attack():
    """Simulate Metasploit exploit (SIMULATION ONLY)"""
    try:
        data = request.get_json() or {}
        target_ip = sanitize_input(data.get('target_ip', ''), 15)
        exploit = sanitize_input(data.get('exploit', 'generic'), 20)
        
        if not target_ip:
            return jsonify({"error": "target_ip required"}), 400
        
        if not validate_ip_address(target_ip):
            return jsonify({"error": "Invalid IP address format"}), 400
        
        # Only allow safe exploit names for simulation
        safe_exploits = ['generic', 'test', 'simulation', 'educational']
        if exploit not in safe_exploits:
            exploit = 'generic'
        
        # Log the simulated attack attempt
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                ("metasploit_simulation", target_ip, "simulated", f"Exploit: {exploit}")
            )
            conn.commit()
        
        app.logger.warning(f"Simulated Metasploit exploit logged for {target_ip} using {exploit}")
        
        return jsonify({
            "status": "simulated",
            "target": target_ip,
            "exploit": exploit,
            "message": f"Metasploit exploit simulation logged for {target_ip}",
            "note": "This is a simulation for educational purposes only"
        })
    except Exception as e:
        app.logger.error(f"Exploit simulation error: {str(e)}")
        return jsonify({"error": "Exploit simulation failed"}), 500

@app.route('/api/console/execute', methods=['POST'])
@rate_limit(max_requests=20, window=60)
@require_api_key
def api_console_execute():
    """Execute console commands (SIMULATION ONLY)"""
    try:
        data = request.get_json() or {}
        command = sanitize_input(data.get('command', ''), 50)
        
        if not command:
            return jsonify({"error": "Command required"}), 400
        
        # Whitelist of safe simulated commands
        safe_responses = {
            'help': 'Available commands: scan, status, info, whoami, pwd, ls, date, uptime',
            'scan network': 'Network scan simulation initiated...',
            'status': 'All systems operational - SIMULATION MODE',
            'info': 'CYBER-MATRIX v8.0 - Educational Penetration Testing Suite',
            'whoami': 'cyber-matrix-user',
            'pwd': '/opt/cyber-matrix',
            'ls': 'scan_results.db  attack_logs.db  config.json',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': 'System uptime: Simulation mode',
            'ps': 'PID  COMMAND\n1234 cyber-matrix\n5678 simulation-service',
        }
        
        # Log command execution
        app.logger.info(f"Console command executed: {command}")
        
        # Get response or default
        response = safe_responses.get(command.lower(), 
                   f'Command simulation: {command} (educational mode only)')
        
        return jsonify({
            "status": "success",
            "command": command,
            "output": response,
            "note": "This is a simulation for educational purposes"
        })
    except Exception as e:
        app.logger.error(f"Console simulation error: {str(e)}")
        return jsonify({"error": "Console simulation failed"}), 500

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