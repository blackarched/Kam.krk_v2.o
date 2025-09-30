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

@app.route('/api/network/scan', methods=['POST'])
def api_network_scan():
    """Initiate network scan"""
    data = request.get_json() or {}
    ip_range = data.get('ip_range', '192.168.1.0/24')
    
    try:
        system_metrics['active_scans'] += 1
        devices = discover_network_devices(ip_range)
        system_metrics['active_scans'] -= 1
        
        # Persist scan results
        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO scan_results (scan_type, target, results, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("network", ip_range, json.dumps(devices), "completed")
                )
                conn.commit()
        except Exception as db_err:
            app.logger.warning(f"Failed to persist network scan results: {db_err}")

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

        # Persist scan results
        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO scan_results (scan_type, target, results, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("port", target_ip, json.dumps(ports), "completed")
                )
                conn.commit()
        except Exception as db_err:
            app.logger.warning(f"Failed to persist port scan results: {db_err}")
        
        return jsonify({
            "status": "success",
            "target": target_ip,
            "open_ports": ports,
            "total_open": len(ports)
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        return jsonify({"error": "Port scan failed"}), 500

@app.route('/api/vulnerability/scan', methods=['POST'])
def api_vulnerability_scan():
    """Basic vulnerability assessment based on open ports and heuristics"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    intensity = (data.get('intensity') or 'medium').lower()

    if not target_ip or not validate_ip_address(target_ip):
        return jsonify({"error": "valid target_ip required"}), 400

    intensity_port_map = {
        'low': '22,80,443',
        'medium': '1-1024',
        'high': '1-2000',
        'aggressive': '1-5000'
    }
    port_range = intensity_port_map.get(intensity, '1-1024')

    try:
        system_metrics['active_scans'] += 1
        open_ports = scan_ports(target_ip, port_range)
        system_metrics['active_scans'] -= 1

        vulnerability_catalog = []
        for entry in open_ports:
            port = entry.get('port')
            service = entry.get('service') or 'unknown'
            severity = 'low'
            if port in (21, 23, 25, 110):
                severity = 'high'
            elif port in (80, 443):
                severity = 'medium'
            elif port in (22,):
                severity = 'medium'
            vulnerability_catalog.append({
                'port': port,
                'service': service,
                'severity': severity,
                'description': f'Open {service.upper()} service on port {port}'
            })

        total_found = len([v for v in vulnerability_catalog if v['severity'] != 'low'])

        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO scan_results (scan_type, target, results, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("vulnerability", target_ip, json.dumps(vulnerability_catalog), "completed")
                )
                conn.commit()
        except Exception as db_err:
            app.logger.warning(f"Failed to persist vulnerability scan results: {db_err}")

        system_metrics['vulnerabilities'] = total_found

        return jsonify({
            'status': 'success',
            'target': target_ip,
            'vulnerabilities': vulnerability_catalog,
            'total_found': total_found
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        return jsonify({"error": "Vulnerability scan failed"}), 500

@app.route('/api/charts/scan_results')
def api_charts_scan_results():
    """Get data for scan results chart from DB metrics"""
    active = 0
    inactive = 0
    vulnerable = 0
    try:
        with get_db_connection() as conn:
            active = conn.execute(
                "SELECT COUNT(*) FROM network_devices WHERE status = 'active'"
            ).fetchone()[0]
            total = conn.execute("SELECT COUNT(*) FROM network_devices").fetchone()[0]
            inactive = max(0, total - active)
            vulnerable = conn.execute(
                "SELECT COUNT(*) FROM network_devices WHERE vulnerability_score > 0"
            ).fetchone()[0]
    except Exception as e:
        app.logger.warning(f"scan_results chart DB error: {e}")

    data = {
        "labels": ["Active Hosts", "Inactive Hosts", "Vulnerable"],
        "datasets": [{
            "data": [active, inactive, vulnerable],
            "backgroundColor": ["#00ff41", "#ff00de", "#c000ff"]
        }]
    }
    return jsonify(data)

@app.route('/api/charts/port_status')
def api_charts_port_status():
    """Get data for port status chart from last port scan results"""
    labels = ["SSH", "HTTP", "HTTPS", "FTP", "SMB", "RDP"]
    service_to_label = { 'ssh': 'SSH', 'http': 'HTTP', 'https': 'HTTPS', 'ftp': 'FTP', 'smb': 'SMB', 'rdp': 'RDP' }
    counts = {label: 0 for label in labels}
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT results FROM scan_results WHERE scan_type = 'port' ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
            if row:
                results = json.loads(row[0])
                for entry in results:
                    service = (entry.get('service') or 'unknown').lower()
                    mapped = service_to_label.get(service)
                    if mapped:
                        counts[mapped] += 1
    except Exception as e:
        app.logger.warning(f"port_status chart DB error: {e}")

    data = {
        "labels": labels,
        "datasets": [{
            "label": "Open Ports",
            "data": [counts[l] for l in labels],
            "backgroundColor": ["#c000ff", "#ff00de", "#00ff41", "#c000ff", "#ff00de", "#00ff41"]
        }]
    }
    return jsonify(data)

@app.route('/api/charts/vulnerability')
def api_charts_vulnerability():
    """Get data for vulnerability radar chart from last vulnerability scan"""
    categories = [
        "Remote Code",
        "Privilege Escalation",
        "Information Disclosure",
        "Denial of Service",
        "Authentication Bypass"
    ]
    values = [0, 0, 0, 0, 0]
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT results FROM scan_results WHERE scan_type = 'vulnerability' ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
            if row:
                vulns = json.loads(row[0])
                severity_counts = {'low': 0, 'medium': 0, 'high': 0}
                for v in vulns:
                    severity = (v.get('severity') or 'low').lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                values = [
                    severity_counts['high'] * 20,
                    severity_counts['medium'] * 15,
                    severity_counts['low'] * 10,
                    max(0, severity_counts['high'] - 1) * 10,
                    max(0, severity_counts['medium'] - 1) * 5
                ]
    except Exception as e:
        app.logger.warning(f"vulnerability chart DB error: {e}")

    data = {
        "labels": categories,
        "datasets": [{
            "label": "Vulnerability Level",
            "data": values,
            "backgroundColor": "rgba(192, 0, 255, 0.2)",
            "borderColor": "#c000ff"
        }]
    }
    return jsonify(data)

@app.route('/api/charts/system_metrics')
def api_charts_system_metrics():
    """Get data for system metrics chart from DB history"""
    labels = []
    cpu_values = []
    mem_values = []
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT timestamp, metric_name, metric_value
                FROM system_metrics
                WHERE metric_name IN ('cpu_usage', 'memory_usage')
                ORDER BY id DESC
                LIMIT 50
                """
            ).fetchall()
            samples = {}
            for row in rows:
                ts = row['timestamp']
                name = row['metric_name']
                val = row['metric_value']
                samples.setdefault(ts, {})[name] = val
            for ts in sorted(samples.keys())[-12:]:
                labels.append(datetime.fromisoformat(ts).strftime('%H:%M'))
                cpu_values.append(samples[ts].get('cpu_usage', 0))
                mem_values.append(samples[ts].get('memory_usage', 0))
    except Exception as e:
        app.logger.warning(f"system_metrics chart DB error: {e}")

    data = {
        "labels": labels,
        "datasets": [
            {
                "label": "CPU Usage",
                "data": cpu_values,
                "borderColor": "#c000ff",
                "backgroundColor": "transparent"
            },
            {
                "label": "Memory Usage",
                "data": mem_values,
                "borderColor": "#ff00de",
                "backgroundColor": "transparent"
            }
        ]
    }
    return jsonify(data)

@app.route('/api/attack/hydra', methods=['POST'])
def api_attack_hydra():
    """Acknowledge Hydra attack request (execution disabled)"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    protocol = (data.get('protocol') or 'ssh').lower()
    if not target_ip or not validate_ip_address(target_ip):
        return jsonify({"error": "valid target_ip required"}), 400
    message = (
        f"Hydra attack requested for {protocol.upper()} on {target_ip}. "
        "Execution is disabled in this environment, request logged."
    )
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                ("hydra", target_ip, "requested", json.dumps({"protocol": protocol}))
            )
            conn.commit()
    except Exception as e:
        app.logger.warning(f"Failed to log hydra attack: {e}")
    return jsonify({"status": "acknowledged", "message": message})

@app.route('/api/attack/metasploit', methods=['POST'])
def api_attack_metasploit():
    """Acknowledge Metasploit exploit request (execution disabled)"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    exploit = (data.get('exploit') or 'generic')
    if not target_ip or not validate_ip_address(target_ip):
        return jsonify({"error": "valid target_ip required"}), 400
    message = (
        f"Metasploit exploit '{exploit}' requested for {target_ip}. "
        "Execution is disabled in this environment, request logged."
    )
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                ("metasploit", target_ip, "requested", json.dumps({"exploit": exploit}))
            )
            conn.commit()
    except Exception as e:
        app.logger.warning(f"Failed to log metasploit attack: {e}")
    return jsonify({"status": "acknowledged", "message": message})

@app.route('/api/console/execute', methods=['POST'])
def api_console_execute():
    """Execute a limited set of safe console commands"""
    data = request.get_json() or {}
    command = (data.get('command') or '').strip()
    if not command:
        return jsonify({"error": "command required"}), 400

    allowed = {
        'date': ['date'],
        'uname': ['uname', '-a'],
        'uptime': ['uptime'],
        'whoami': ['whoami']
    }

    if command.startswith('echo '):
        text = command[5:].strip()
        return jsonify({"output": text})

    if command in allowed:
        stdout, stderr = run_command(allowed[command])
        output = (stdout or '').strip() or (stderr or '').strip() or '(no output)'
        return jsonify({"output": output})

    return jsonify({"error": "command not allowed"}), 400

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