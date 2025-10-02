#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite
Unified Backend API Server (FIXED VERSION)

This is the main application that serves the dashboard and provides all API endpoints
for network scanning, vulnerability assessment, and penetration testing operations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import re
import os
import json
import time
import threading
import psutil
import ipaddress
from datetime import datetime, timedelta
import secrets
import sqlite3
from contextlib import contextmanager
import logging
from logging.handlers import RotatingFileHandler
import signal
import sys
import shlex
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app FIRST (before any app.logger calls)
app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

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

# Now safely import optional dependencies
try:
    from secure_network_tools import secure_tools
    SECURE_TOOLS_AVAILABLE = True
except ImportError:
    SECURE_TOOLS_AVAILABLE = False
    print("Warning: Secure network tools not available. Using fallback methods.")

try:
    import netifaces as ni
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    print("Warning: netifaces not available. Using alternative methods.")

# Bluetooth support disabled for security
BLUETOOTH_AVAILABLE = False
print("Info: Bluetooth support disabled for security reasons.")

# Scapy disabled for security
SCAPY_AVAILABLE = False
print("Info: Scapy support disabled for security reasons.")

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
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('PRAGMA foreign_keys=ON')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    scan_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    results TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS network_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT,
                    hostname TEXT,
                    device_type TEXT DEFAULT 'Unknown',
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    vulnerability_score INTEGER DEFAULT 0
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS attack_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    attack_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL
                )
            ''')
            
            conn.commit()
            app.logger.info("Database initialized successfully")
            
    except Exception as e:
        print(f"Database initialization error: {str(e)}")

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
    sanitized = re.sub(r'[;&|`$(){}\\[\\]<>"\']', '', input_str)
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

def run_command(command, timeout=30):
    """Execute system commands safely with timeout"""
    try:
        # Always use list format and never shell=True
        if isinstance(command, str):
            command = shlex.split(command)
        
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout
        )
        return result.stdout, result.stderr
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
        try:
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
            print(f"Database error: {str(e)}")
            
    except Exception as e:
        print(f"Error getting system metrics: {str(e)}")

def update_metrics_thread():
    """Background thread to update system metrics"""
    while True:
        try:
            get_system_metrics()
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Metrics thread error: {str(e)}")
            time.sleep(10)  # Wait longer on error

def discover_network_devices(ip_range="192.168.1.0/24"):
    """Discover devices on the network"""
    devices = []
    
    try:
        # Validate IP range
        if not validate_cidr_range(ip_range):
            print(f"Invalid IP range: {ip_range}")
            return []
        
        # Method 1: ARP table
        stdout, stderr = run_command(["arp", "-a"])
        if stdout:
            for line in stdout.splitlines():
                match = re.search(r"\\(([\\d.]+)\\) at ([a-fA-F0-9:]+)", line)
                if match:
                    ip, mac = match.groups()
                    if validate_ip_address(ip):
                        devices.append({
                            "ip": ip,
                            "mac": mac,
                            "hostname": "Unknown",
                            "method": "ARP",
                            "status": "active"
                        })
        
        # Store in database
        try:
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
        except Exception as e:
            print(f"Database error: {str(e)}")
        
        system_metrics['devices_found'] = len(devices)
        return devices
        
    except Exception as e:
        print(f"Error in network discovery: {str(e)}")
        return []

def scan_ports(target_ip, port_range="22,80,443"):
    """Scan ports on target IP"""
    try:
        if not validate_ip_address(target_ip):
            return []
        
        if not validate_port_range(port_range):
            return []
        
        open_ports = []
        
        # Parse ports
        if ',' in port_range:
            ports = [int(p.strip()) for p in port_range.split(',')]
        elif '-' in port_range:
            start, end = map(int, port_range.split('-'))
            ports = list(range(start, min(end + 1, start + 100)))
        else:
            ports = [int(port_range)]
        
        # Scan ports
        for port in ports[:20]:  # Limit to 20 ports
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    service_map = {22: "ssh", 80: "http", 443: "https"}
                    service = service_map.get(port, "unknown")
                    open_ports.append({"port": port, "service": service, "state": "open"})
                sock.close()
            except Exception:
                continue
        
        return open_ports
        
    except Exception as e:
        print(f"Error in port scanning: {str(e)}")
        return []

# Network interface utilities
def _get_wireless_interface_info():
    """Parse `iw dev` output to map interface -> type (e.g., managed/monitor)."""
    iw_info = {}
    try:
        stdout, stderr = run_command(["iw", "dev"], timeout=10)
        if not stdout:
            return iw_info
        current = None
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if line.startswith("Interface "):
                parts = line.split()
                if len(parts) >= 2:
                    current = parts[1]
                    iw_info[current] = {"type": None}
            elif line.startswith("type ") and current:
                parts = line.split()
                if len(parts) >= 2:
                    iw_info[current]["type"] = parts[1]
    except Exception:
        pass
    return iw_info

def _wireless_monitor_supported():
    """Check whether the system supports monitor mode at all (via `iw list`)."""
    try:
        stdout, stderr = run_command(["iw", "list"], timeout=10)
        if stdout and "* monitor" in stdout:
            return True
    except Exception:
        return False
    return False

def list_network_interfaces():
    """List network interfaces with status and basic attributes."""
    interfaces = []
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        iw_info = _get_wireless_interface_info()
        monitor_supported_global = _wireless_monitor_supported()
        for name, stat in stats.items():
            iface_addrs = addrs.get(name, [])
            ipv4 = None
            ipv6 = None
            mac = None
            for addr in iface_addrs:
                # psutil returns family enums; string compare fallback
                fam = getattr(addr, 'family', None)
                fam_str = str(fam)
                if fam_str.endswith('AF_LINK') and not mac:
                    mac = addr.address
                elif fam_str.endswith('AF_INET') and not ipv4:
                    ipv4 = addr.address
                elif fam_str.endswith('AF_INET6') and not ipv6:
                    ipv6 = addr.address
            # Heuristic for type
            lowered = name.lower()
            if lowered.startswith('wl') or lowered.startswith('wlan'):
                iface_type = 'wireless'
            elif lowered == 'lo':
                iface_type = 'loopback'
            elif lowered.startswith('eth') or lowered.startswith('en'):
                iface_type = 'ethernet'
            else:
                iface_type = 'other'
            iw = iw_info.get(name, {})
            monitor_enabled = iw.get('type') == 'monitor'
            interfaces.append({
                "name": name,
                "is_up": bool(getattr(stat, 'isup', False)),
                "mtu": getattr(stat, 'mtu', None),
                "speed_mbps": getattr(stat, 'speed', None),
                "duplex": getattr(stat, 'duplex', None),
                "ipv4": ipv4 or "",
                "ipv6": ipv6 or "",
                "mac": mac or "",
                "type": iface_type,
                "monitor_supported": monitor_supported_global and iface_type == 'wireless',
                "monitor_enabled": monitor_enabled
            })
    except Exception as e:
        print(f"Error listing interfaces: {str(e)}")
    return interfaces

# API: Network interfaces
@app.route('/api/network/interfaces', methods=['GET'])
def api_network_interfaces():
    try:
        return jsonify({"interfaces": list_network_interfaces()})
    except Exception:
        return jsonify({"interfaces": []}), 200

@app.route('/api/network/monitor', methods=['POST'])
def api_network_monitor():
    data = request.get_json() or {}
    iface = sanitize_input(str(data.get('interface', '')))
    enable = bool(data.get('enable', True))
    if not iface:
        return jsonify({"error": "interface required"}), 400
    # Validate interface exists
    known = {i['name'] for i in list_network_interfaces()}
    if iface not in known:
        return jsonify({"error": "unknown interface"}), 404
    # Attempt monitor toggle
    try:
        # Bring down
        run_command(["ip", "link", "set", iface, "down"], timeout=10)
        if enable:
            # Enable monitor
            stdout, stderr = run_command(["iw", "dev", iface, "set", "type", "monitor"], timeout=10)
        else:
            # Back to managed
            stdout, stderr = run_command(["iw", "dev", iface, "set", "type", "managed"], timeout=10)
        # Bring up
        run_command(["ip", "link", "set", iface, "up"], timeout=10)
        # Report new state
        iw_info = _get_wireless_interface_info()
        monitor_enabled = iw_info.get(iface, {}).get('type') == 'monitor'
        return jsonify({
            "status": "success",
            "interface": iface,
            "monitor_enabled": monitor_enabled
        })
    except Exception as e:
        return jsonify({"error": "failed to toggle monitor mode. try running as root."}), 500

# API Routes
@app.route('/')
def index():
    """Serve the main dashboard"""
    try:
        with open('kamkrk_v2.html', 'r') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Dashboard file not found", 404

@app.route('/api/system/metrics')
def api_system_metrics():
    """Get current system metrics"""
    return jsonify(system_metrics)

@app.route('/api/auth/generate_key', methods=['POST'])
def api_generate_key():
    """Generate a new API key"""
    try:
        new_key = secrets.token_urlsafe(32)
        global API_KEY_HASH
        API_KEY_HASH = generate_password_hash(new_key)
        
        return jsonify({
            "status": "success",
            "api_key": new_key,
            "message": "New API key generated successfully"
        })
    except Exception as e:
        return jsonify({"error": "Failed to generate API key"}), 500

@app.route('/api/auth/validate_key', methods=['POST'])
def api_validate_key():
    """Validate an API key"""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({"error": "API key required"}), 400
        
        is_valid = check_password_hash(API_KEY_HASH, api_key)
        
        return jsonify({
            "status": "success",
            "valid": is_valid,
            "message": "API key validated" if is_valid else "Invalid API key"
        })
    except Exception as e:
        return jsonify({"error": "Failed to validate API key"}), 500

@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    """Check API authentication status"""
    try:
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        is_authenticated = api_key and check_password_hash(API_KEY_HASH, api_key)
        
        return jsonify({
            "authenticated": is_authenticated,
            "message": "API authenticated" if is_authenticated else "API not authenticated"
        })
    except Exception as e:
        return jsonify({"error": "Failed to check auth status"}), 500

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
        return jsonify({"error": "Network scan failed"}), 500

@app.route('/api/port/scan', methods=['POST'])
def api_port_scan():
    """Initiate port scan"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    port_range = data.get('port_range', '22,80,443')
    
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
        return jsonify({"error": "Port scan failed"}), 500

@app.route('/api/charts/scan_results')
def api_charts_scan_results():
    """Get data for scan results chart"""
    data = {
        "labels": ["Active Hosts", "Inactive Hosts", "Vulnerable"],
        "datasets": [{
            "data": [
                system_metrics['devices_found'],
                1,  # Minimal fallback
                system_metrics['vulnerabilities']
            ],
            "backgroundColor": ["#00ff41", "#ff00de", "#c000ff"]
        }]
    }
    return jsonify(data)

@app.route('/api/charts/port_status')
def api_charts_port_status():
    """Get data for port status chart"""
    try:
        # Get real port scan data from database
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT results FROM scan_results 
                WHERE scan_type = 'port_scan' 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            
            if result:
                # Parse real scan results
                scan_data = json.loads(result['results'])
                port_counts = {}
                for port_info in scan_data.get('open_ports', []):
                    service = port_info.get('service', 'unknown')
                    port_counts[service] = port_counts.get(service, 0) + 1
                
                labels = list(port_counts.keys())
                data_values = list(port_counts.values())
            else:
                # No data available
                labels = []
                data_values = []
        
        data = {
            "labels": labels,
            "datasets": [{
                "label": "Open Ports",
                "data": data_values,
                "backgroundColor": ["#c000ff", "#ff00de", "#00ff41", "#c000ff", "#ff00de", "#00ff41"]
            }]
        }
        return jsonify(data)
    except Exception as e:
        # Return empty data on error
        return jsonify({
            "labels": [],
            "datasets": [{
                "label": "Open Ports",
                "data": [],
                "backgroundColor": []
            }]
        })

@app.route('/api/charts/vulnerability')
def api_charts_vulnerability():
    """Get data for vulnerability radar chart"""
    try:
        # Get real vulnerability data from database
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT results FROM scan_results 
                WHERE scan_type = 'vulnerability_scan' 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            results = cursor.fetchall()
            
            # Initialize vulnerability categories
            vuln_categories = {
                "Remote Code": 0,
                "Privilege Escalation": 0, 
                "Information Disclosure": 0,
                "Denial of Service": 0,
                "Authentication Bypass": 0
            }
            
            # Process real vulnerability data
            for result in results:
                try:
                    scan_data = json.loads(result['results'])
                    vulnerabilities = scan_data.get('vulnerabilities', [])
                    for vuln in vulnerabilities:
                        vuln_type = vuln.get('type', 'Unknown')
                        severity = vuln.get('severity', 'low')
                        
                        # Map vulnerability types to categories
                        if 'code' in vuln_type.lower() or 'execution' in vuln_type.lower():
                            vuln_categories["Remote Code"] += 1 if severity == 'high' else 0.5
                        elif 'privilege' in vuln_type.lower() or 'escalation' in vuln_type.lower():
                            vuln_categories["Privilege Escalation"] += 1 if severity == 'high' else 0.5
                        elif 'disclosure' in vuln_type.lower() or 'information' in vuln_type.lower():
                            vuln_categories["Information Disclosure"] += 1 if severity == 'high' else 0.5
                        elif 'dos' in vuln_type.lower() or 'denial' in vuln_type.lower():
                            vuln_categories["Denial of Service"] += 1 if severity == 'high' else 0.5
                        elif 'auth' in vuln_type.lower() or 'bypass' in vuln_type.lower():
                            vuln_categories["Authentication Bypass"] += 1 if severity == 'high' else 0.5
                except:
                    continue
        
        data = {
            "labels": list(vuln_categories.keys()),
            "datasets": [{
                "label": "Vulnerability Level",
                "data": list(vuln_categories.values()),
                "backgroundColor": "rgba(192, 0, 255, 0.2)",
                "borderColor": "#c000ff"
            }]
        }
        return jsonify(data)
    except Exception as e:
        # Return empty data on error
        return jsonify({
            "labels": ["Remote Code", "Privilege Escalation", "Information Disclosure", "Denial of Service", "Authentication Bypass"],
            "datasets": [{
                "label": "Vulnerability Level",
                "data": [0, 0, 0, 0, 0],
                "backgroundColor": "rgba(192, 0, 255, 0.2)",
                "borderColor": "#c000ff"
            }]
        })

@app.route('/api/charts/system_metrics')
def api_charts_system_metrics():
    """Get data for system metrics chart"""
    try:
        # Get real system metrics from database
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT metric_name, metric_value, timestamp 
                FROM system_metrics 
                WHERE timestamp > datetime('now', '-2 hours')
                ORDER BY timestamp DESC
                LIMIT 50
            ''')
            results = cursor.fetchall()
            
            # Process metrics data
            cpu_data = []
            memory_data = []
            timestamps = []
            
            # Group by timestamp and extract values
            metrics_by_time = {}
            for result in results:
                timestamp = result['timestamp']
                metric_name = result['metric_name']
                metric_value = result['metric_value']
                
                if timestamp not in metrics_by_time:
                    metrics_by_time[timestamp] = {}
                metrics_by_time[timestamp][metric_name] = metric_value
            
            # Sort by timestamp and create arrays
            sorted_times = sorted(metrics_by_time.keys())[-7:]  # Last 7 data points
            
            for timestamp in sorted_times:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                timestamps.append(time_str)
                
                metrics = metrics_by_time[timestamp]
                cpu_data.append(metrics.get('cpu_usage', 0))
                memory_data.append(metrics.get('memory_usage', 0))
        
        # If no data, use current metrics
        if not timestamps:
            now = datetime.now()
            timestamps = [(now - timedelta(minutes=x*15)).strftime("%H:%M") for x in range(6, -1, -1)]
            cpu_data = [system_metrics.get('cpu_usage', 0)] * 7
            memory_data = [system_metrics.get('memory_usage', 0)] * 7
        
        data = {
            "labels": timestamps,
            "datasets": [
                {
                    "label": "CPU Usage",
                    "data": cpu_data,
                    "borderColor": "#c000ff",
                    "backgroundColor": "transparent"
                },
                {
                    "label": "Memory Usage", 
                    "data": memory_data,
                    "borderColor": "#ff00de",
                    "backgroundColor": "transparent"
                }
            ]
        }
        return jsonify(data)
    except Exception as e:
        # Return current metrics as fallback
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=x*15)).strftime("%H:%M") for x in range(6, -1, -1)]
        
        return jsonify({
            "labels": timestamps,
            "datasets": [
                {
                    "label": "CPU Usage",
                    "data": [system_metrics.get('cpu_usage', 0)] * 7,
                    "borderColor": "#c000ff",
                    "backgroundColor": "transparent"
                },
                {
                    "label": "Memory Usage",
                    "data": [system_metrics.get('memory_usage', 0)] * 7,
                    "borderColor": "#ff00de", 
                    "backgroundColor": "transparent"
                }
            ]
        })

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\\nShutting down CYBER-MATRIX server...")
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
    print("🌐 Dashboard will be available at: http://127.0.0.1:5000")
    print("🔒 API endpoints active and ready")
    print("⚡ Real-time metrics enabled")
    
    # Run the Flask app with secure configuration
    host = os.environ.get('CYBER_MATRIX_HOST', '127.0.0.1')
    port = int(os.environ.get('CYBER_MATRIX_PORT', '5000'))
    
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )