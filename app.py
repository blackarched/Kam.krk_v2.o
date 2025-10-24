#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite
Unified Backend API Server (FIXED VERSION)

This is the main application that serves the dashboard and provides all API endpoints
for network scanning, vulnerability assessment, and penetration testing operations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
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
from network_interface_manager import network_manager

# Initialize Flask app FIRST (before any app.logger calls)
app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

# Initialize SocketIO for WebSocket support
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5000', 'http://127.0.0.1:5000'], async_mode='threading')

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
    'vulnerabilities': 0,
    'threat_level': 25.5,
    'vulnerability_index': 18.7,
    'encryption_strength': 87.3,
    'network_health': 94.2
}

# Global scan progress tracking
scan_progress = {
    'current_scan': None,
    'progress': 0,
    'status': 'idle',
    'message': '',
    'start_time': None,
    'results': None
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

        # Calculate derived metrics
        # Threat level based on vulnerabilities and active scans
        base_threat = system_metrics['vulnerabilities'] * 2 + system_metrics['active_scans'] * 5
        system_metrics['threat_level'] = min(100, base_threat + (system_metrics['cpu_usage'] + system_metrics['memory_usage']) / 4)

        # Vulnerability index based on found vulnerabilities and network health
        system_metrics['vulnerability_index'] = min(100, system_metrics['vulnerabilities'] * 3 + (100 - system_metrics['network_health']) / 2)

        # Encryption strength (simulated based on system state)
        system_metrics['encryption_strength'] = max(50, 100 - system_metrics['threat_level'] / 2)

        # Network health based on devices found and network traffic
        system_metrics['network_health'] = max(0, 100 - system_metrics['threats_detected'] * 2 - system_metrics['network_traffic'] / 2)

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
                conn.execute(
                    "INSERT INTO system_metrics (metric_name, metric_value) VALUES (?, ?)",
                    ("threat_level", system_metrics['threat_level'])
                )
                conn.execute(
                    "INSERT INTO system_metrics (metric_name, metric_value) VALUES (?, ?)",
                    ("vulnerability_index", system_metrics['vulnerability_index'])
                )
                conn.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")

    except Exception as e:
        print(f"Error getting system metrics: {str(e)}")

def update_scan_progress(progress, message):
    """Update global scan progress"""
    global scan_progress
    scan_progress['progress'] = progress
    scan_progress['message'] = message
    scan_progress['status'] = 'running' if progress < 100 else 'completed'

def network_scan_worker(ip_range):
    """Background worker for network scanning"""
    global scan_progress
    try:
        scan_progress['start_time'] = datetime.now()
        scan_progress['status'] = 'running'
        scan_progress['current_scan'] = 'network_scan'

        devices = discover_network_devices(ip_range, update_scan_progress)

        scan_progress['results'] = devices
        scan_progress['progress'] = 100
        scan_progress['status'] = 'completed'
        scan_progress['message'] = f"Scan completed successfully. Found {len(devices)} devices."

    except Exception as e:
        scan_progress['status'] = 'failed'
        scan_progress['message'] = f"Scan failed: {str(e)}"
        scan_progress['progress'] = 0

def update_metrics_thread():
    """Background thread to update system metrics"""
    while True:
        try:
            get_system_metrics()
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Metrics thread error: {str(e)}")
            time.sleep(10)  # Wait longer on error

def discover_network_devices(ip_range="192.168.1.0/24", progress_callback=None):
    """Discover devices on the network with enhanced scanning and progress tracking"""
    devices = []

    try:
        # Validate IP range
        if not validate_cidr_range(ip_range):
            raise ValueError(f"Invalid IP range: {ip_range}")

        if progress_callback:
            progress_callback(10, "Initializing network scan...")

        # Method 1: ARP table scan
        if progress_callback:
            progress_callback(20, "Scanning ARP table...")

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
                            "status": "active",
                            "last_seen": datetime.now().isoformat()
                        })

        # Method 2: Enhanced ping sweep if nmap available
        try:
            import subprocess
            if progress_callback:
                progress_callback(40, "Performing ping sweep...")

            # Try nmap ping scan
            nmap_cmd = ["nmap", "-sn", "-T4", "--max-retries", "1", ip_range]
            stdout, stderr = run_command(nmap_cmd)

            if stdout:
                # Parse nmap output for additional devices
                for line in stdout.splitlines():
                    if "Nmap scan report for" in line:
                        # Extract IP from nmap output
                        ip_match = re.search(r"\\(([\\d.]+)\\)", line)
                        if ip_match:
                            ip = ip_match.group(1)
                            if validate_ip_address(ip) and not any(d['ip'] == ip for d in devices):
                                devices.append({
                                    "ip": ip,
                                    "mac": "Unknown",
                                    "hostname": "Unknown",
                                    "method": "Nmap",
                                    "status": "active",
                                    "last_seen": datetime.now().isoformat()
                                })
        except Exception as e:
            print(f"Nmap scan failed, continuing with ARP results: {str(e)}")

        # Method 3: DNS resolution for hostnames
        if progress_callback:
            progress_callback(70, "Resolving hostnames...")

        for device in devices:
            if device['hostname'] == "Unknown":
                try:
                    import socket
                    hostname = socket.gethostbyaddr(device['ip'])[0]
                    device['hostname'] = hostname
                except:
                    pass  # Keep as Unknown

        # Method 4: Port scan for basic service detection
        if progress_callback:
            progress_callback(85, "Detecting services...")

        for device in devices[:10]:  # Limit to first 10 devices for performance
            try:
                open_ports = scan_ports(device['ip'], "22,80,443")
                if open_ports:
                    device['services'] = open_ports
                    device['device_type'] = "Server/Network Device"
                else:
                    device['device_type'] = "End Device"
            except:
                device['device_type'] = "Unknown"

        if progress_callback:
            progress_callback(95, "Storing results...")

        # Store in database
        try:
            with get_db_connection() as conn:
                for device in devices:
                    conn.execute('''
                        INSERT OR REPLACE INTO network_devices
                        (ip_address, mac_address, hostname, device_type, status, last_seen, vulnerability_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        device.get('ip', ''),
                        device.get('mac', ''),
                        device.get('hostname', ''),
                        device.get('device_type', 'Unknown'),
                        device.get('status', 'active'),
                        device.get('last_seen', datetime.now().isoformat()),
                        0  # Default vulnerability score
                    ))
                conn.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")

        system_metrics['devices_found'] = len(devices)

        if progress_callback:
            progress_callback(100, f"Scan completed. Found {len(devices)} devices.")

        return devices

    except Exception as e:
        error_msg = f"Error in network discovery: {str(e)}"
        print(error_msg)
        if progress_callback:
            progress_callback(0, f"Scan failed: {str(e)}")
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

# Network interface utilities - Enhanced with NetworkInterfaceManager
def list_network_interfaces():
    """List network interfaces with status and basic attributes using NetworkInterfaceManager."""
    try:
        # Refresh interfaces to get latest data
        interfaces_data = network_manager.refresh_interfaces()
        
        # Convert to the expected format for API compatibility
        interfaces = []
        for name, data in interfaces_data.items():
            interfaces.append({
                "name": data['name'],
                "is_up": data['is_up'],
                "mtu": None,  # Not provided by new manager, could be added if needed
                "speed_mbps": None,  # Not provided by new manager
                "duplex": None,  # Not provided by new manager
                "ipv4": data['ipv4'],
                "ipv6": data['ipv6'],
                "mac": data['mac'],
                "type": data['type'],
                "mode": data['mode'],
                "is_wireless": data['is_wireless'],
                "monitor_supported": data['monitor_supported'],
                "monitor_enabled": data['is_monitor'],
                "flags": data['flags'],
                "last_updated": data['last_updated']
            })
        
        return interfaces
    except Exception as e:
        print(f"Error listing interfaces: {str(e)}")
        return []

# API: Network interfaces
@app.route('/api/network/interfaces', methods=['GET'])
def api_network_interfaces():
    try:
        return jsonify({"interfaces": list_network_interfaces()})
    except Exception:
        return jsonify({"interfaces": []}), 200

@app.route('/api/network/monitor', methods=['POST'])
def api_network_monitor():
    """Toggle monitor mode using the sophisticated NetworkInterfaceManager."""
    data = request.get_json() or {}
    iface = sanitize_input(str(data.get('interface', '')))
    enable = bool(data.get('enable', True))
    
    if not iface:
        return jsonify({"error": "interface required"}), 400
    
    try:
        # Use NetworkInterfaceManager for sophisticated monitor mode handling
        success, error_msg = network_manager.toggle_monitor_mode(iface, enable)
        
        if success:
            # Get updated interface data
            updated_data = network_manager.get_interface_data(iface)
            return jsonify({
                "status": "success",
                "interface": iface,
                "monitor_enabled": updated_data['is_monitor'] if updated_data else enable,
                "mode": updated_data['mode'] if updated_data else ('monitor' if enable else 'managed'),
                "message": f"Monitor mode {'enabled' if enable else 'disabled'} on {iface}"
            })
        else:
            return jsonify({
                "error": error_msg,
                "interface": iface,
                "monitor_enabled": False
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": f"Failed to toggle monitor mode: {str(e)}",
            "interface": iface
        }), 500

@app.route('/api/network/interfaces/refresh', methods=['POST'])
def api_refresh_interfaces():
    """Force refresh of network interfaces."""
    try:
        interfaces_data = network_manager.refresh_interfaces()
        return jsonify({
            "status": "success",
            "message": "Interfaces refreshed successfully",
            "interfaces": list_network_interfaces(),
            "summary": network_manager.get_interface_status_summary()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to refresh interfaces: {str(e)}"}), 500

@app.route('/api/network/interfaces/summary', methods=['GET'])
def api_interface_summary():
    """Get interface status summary for dashboard."""
    try:
        summary = network_manager.get_interface_status_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": f"Failed to get interface summary: {str(e)}"}), 500

@app.route('/api/network/interfaces/<interface_name>', methods=['GET'])
def api_interface_details(interface_name):
    """Get detailed information about a specific interface."""
    try:
        interface_name = sanitize_input(interface_name)
        data = network_manager.get_interface_data(interface_name)
        
        if data:
            return jsonify({
                "status": "success",
                "interface": data
            })
        else:
            return jsonify({"error": "Interface not found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Failed to get interface details: {str(e)}"}), 500

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

@app.route('/api/auth/generate-key', methods=['POST'])
def api_generate_key():
    """Generate a new API key"""
    try:
        new_api_key = secrets.token_urlsafe(32)
        # DO NOT update the hash here. The key is only activated when the user clicks "ACTIVATE".
        # This was the source of the bug.
        return jsonify({
            "status": "success",
            "api_key": new_api_key,
            "message": "New API key generated. Please activate it."
        })
    except Exception as e:
        return jsonify({"error": "Failed to generate API key"}), 500

@app.route('/api/auth/activate', methods=['POST'])
def api_activate_key():
    """Activates a new API key"""
    data = request.get_json() or {}
    api_key = data.get('api_key')

    if not api_key or not isinstance(api_key, str) or len(api_key) < 32:
         return jsonify({"error": "A valid API key must be provided for activation"}), 400

    try:
        global API_KEY_HASH
        API_KEY_HASH = generate_password_hash(api_key)
        
        return jsonify({
            "status": "success",
            "message": "API key activated successfully"
        })
    except Exception as e:
        app.logger.error(f"API key activation failed: {str(e)}")
        return jsonify({"error": "Failed to activate API key"}), 500


@app.route('/api/auth/verify', methods=['GET'])
@require_api_key
def api_verify_key():
    """Verify provided API key is valid"""
    return jsonify({
        "status": "success",
        "message": "API key is valid"
    })

@app.route('/api/system/metrics')
def api_system_metrics():
    """Get current system metrics"""
    return jsonify(system_metrics)

@app.route('/api/network/scan', methods=['POST'])
@require_api_key
def api_network_scan():
    """Initiate asynchronous network scan with progress tracking"""
    global scan_progress

    data = request.get_json() or {}
    ip_range = data.get('ip_range', '192.168.1.0/24')

    # Check if scan is already running
    if scan_progress['status'] == 'running':
        return jsonify({
            "error": "Scan already in progress",
            "progress": scan_progress
        }), 409

    try:
        # Reset progress
        scan_progress.update({
            'current_scan': 'network_scan',
            'progress': 0,
            'status': 'starting',
            'message': 'Initializing scan...',
            'start_time': datetime.now().isoformat(),
            'results': None
        })

        system_metrics['active_scans'] += 1

        # Start scan in background thread
        scan_thread = threading.Thread(target=network_scan_worker, args=(ip_range,))
        scan_thread.daemon = True
        scan_thread.start()

        return jsonify({
            "status": "started",
            "message": "Network scan initiated",
            "scan_id": "network_scan",
            "progress": scan_progress
        })

    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        scan_progress['status'] = 'failed'
        scan_progress['message'] = f"Failed to start scan: {str(e)}"
        return jsonify({"error": f"Failed to start network scan: {str(e)}"}), 500

@app.route('/api/scan/progress', methods=['GET'])
@require_api_key
def api_scan_progress():
    """Get current scan progress"""
    global scan_progress

    # If scan completed, return final results
    if scan_progress['status'] == 'completed' and scan_progress['results'] is not None:
        devices = scan_progress['results']
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)

        # Store final results in database
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                    ("network_scan", "async_scan", json.dumps({"devices": devices, "total_found": len(devices)}), "completed")
                )
                conn.commit()
        except Exception as e:
            print(f"Database error storing final results: {str(e)}")

        # Reset progress after returning results
        result = dict(scan_progress)
        scan_progress.update({
            'current_scan': None,
            'progress': 0,
            'status': 'idle',
            'message': '',
            'start_time': None,
            'results': None
        })

        return jsonify({
            "status": "completed",
            "progress": 100,
            "message": result['message'],
            "devices": devices,
            "total_found": len(devices)
        })

    return jsonify(scan_progress)

@app.route('/api/port/scan', methods=['POST'])
@require_api_key
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
        
        # Store scan results in database
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                    ("port_scan", target_ip, json.dumps({"open_ports": ports, "total_open": len(ports)}), "completed")
                )
                conn.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")
        
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
            cursor = conn.execute("""
                SELECT results FROM scan_results 
                WHERE scan_type = 'port_scan' 
                ORDER BY timestamp DESC LIMIT 1
            """)
            result = cursor.fetchone()
            
        if result:
            import json
            scan_data = json.loads(result['results'])
            port_counts = {}
            
            # Count open ports by service
            for port_info in scan_data.get('open_ports', []):
                service = port_info.get('service', 'unknown').upper()
                port_counts[service] = port_counts.get(service, 0) + 1
            
            labels = list(port_counts.keys()) or ["No Data"]
            data_values = list(port_counts.values()) or [0]
        else:
            labels = ["No Scans"]
            data_values = [0]
        
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
            "labels": ["No Data"],
            "datasets": [{
                "label": "Open Ports",
                "data": [0],
                "backgroundColor": ["#666666"]
            }]
        })

@app.route('/api/charts/vulnerability')
def api_charts_vulnerability():
    """Get data for vulnerability radar chart"""
    try:
        # Get real vulnerability data from database
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT results FROM scan_results 
                WHERE scan_type = 'vulnerability_scan' 
                ORDER BY timestamp DESC LIMIT 1
            """)
            result = cursor.fetchone()
            
        if result:
            import json
            vuln_data = json.loads(result['results'])
            vuln_counts = vuln_data.get('vulnerability_counts', {})
            
            labels = ["Remote Code", "Privilege Escalation", "Information Disclosure", "Denial of Service", "Authentication Bypass"]
            data_values = [
                vuln_counts.get('remote_code', 0),
                vuln_counts.get('privilege_escalation', 0),
                vuln_counts.get('information_disclosure', 0),
                vuln_counts.get('denial_of_service', 0),
                vuln_counts.get('authentication_bypass', 0)
            ]
        else:
            labels = ["Remote Code", "Privilege Escalation", "Information Disclosure", "Denial of Service", "Authentication Bypass"]
            data_values = [0, 0, 0, 0, 0]
        
        data = {
            "labels": labels,
            "datasets": [{
                "label": "Vulnerability Level",
                "data": data_values,
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
            cursor = conn.execute("""
                SELECT metric_name, metric_value, timestamp 
                FROM system_metrics 
                WHERE timestamp > datetime('now', '-2 hours')
                ORDER BY timestamp DESC
                LIMIT 14
            """)
            results = cursor.fetchall()
        
        # Process the data
        cpu_data = []
        memory_data = []
        timestamps = []
        
        if results:
            # Group by timestamp and get latest values
            data_points = {}
            for row in results:
                ts = row['timestamp'][:16]  # Get HH:MM format
                if ts not in data_points:
                    data_points[ts] = {}
                data_points[ts][row['metric_name']] = row['metric_value']
            
            # Sort by timestamp and take last 7 points
            sorted_times = sorted(data_points.keys())[-7:]
            for ts in sorted_times:
                timestamps.append(ts[-5:])  # Get just HH:MM
                cpu_data.append(data_points[ts].get('cpu_usage', 0))
                memory_data.append(data_points[ts].get('memory_usage', 0))
        
        # If no data, create empty chart
        if not timestamps:
            now = datetime.now()
            timestamps = [(now - timedelta(minutes=x*15)).strftime("%H:%M") for x in range(6, -1, -1)]
            cpu_data = [0] * 7
            memory_data = [0] * 7
        
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
        # Return empty data on error
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=x*15)).strftime("%H:%M") for x in range(6, -1, -1)]
        return jsonify({
            "labels": timestamps,
            "datasets": [
                {
                    "label": "CPU Usage",
                    "data": [0] * 7,
                    "borderColor": "#c000ff",
                    "backgroundColor": "transparent"
                },
                {
                    "label": "Memory Usage",
                    "data": [0] * 7,
                    "borderColor": "#ff00de",
                    "backgroundColor": "transparent"
                }
            ]
        })

@app.route('/api/vulnerability/scan', methods=['POST'])
@require_api_key
def api_vulnerability_scan():
    """Initiate vulnerability scan"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    intensity = data.get('intensity', 'medium')
    
    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400
    
    if not validate_ip_address(target_ip):
        return jsonify({"error": "Invalid IP address format"}), 400
    
    try:
        system_metrics['active_scans'] += 1
        
        # Simulate vulnerability scanning (replace with real tools in production)
        vulnerabilities = []
        vulnerability_counts = {
            'remote_code': 0,
            'privilege_escalation': 0,
            'information_disclosure': 0,
            'denial_of_service': 0,
            'authentication_bypass': 0
        }
        
        # Basic port-based vulnerability checks
        ports = scan_ports(target_ip, "21,22,23,25,53,80,110,143,443,993,995")
        for port_info in ports:
            port = port_info['port']
            service = port_info['service']
            
            # Simple vulnerability detection based on open ports
            if port == 21:  # FTP
                vulnerabilities.append({"type": "information_disclosure", "severity": "medium", "description": "FTP service detected"})
                vulnerability_counts['information_disclosure'] += 1
            elif port == 23:  # Telnet
                vulnerabilities.append({"type": "authentication_bypass", "severity": "high", "description": "Insecure Telnet service"})
                vulnerability_counts['authentication_bypass'] += 1
            elif port == 80 and service == 'http':
                vulnerabilities.append({"type": "information_disclosure", "severity": "low", "description": "Unencrypted HTTP service"})
                vulnerability_counts['information_disclosure'] += 1
        
        system_metrics['active_scans'] -= 1
        system_metrics['vulnerabilities'] = len(vulnerabilities)
        
        # Store results in database
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                    ("vulnerability_scan", target_ip, json.dumps({
                        "vulnerabilities": vulnerabilities,
                        "vulnerability_counts": vulnerability_counts,
                        "total_found": len(vulnerabilities)
                    }), "completed")
                )
                conn.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")
        
        return jsonify({
            "status": "success",
            "target": target_ip,
            "vulnerabilities": vulnerabilities,
            "total_found": len(vulnerabilities)
        })
    except Exception as e:
        system_metrics['active_scans'] = max(0, system_metrics['active_scans'] - 1)
        return jsonify({"error": "Vulnerability scan failed"}), 500

@app.route('/api/attack/hydra', methods=['POST'])
@require_api_key
def api_attack_hydra():
    """Simulate Hydra brute force attack with detailed logging and safety checks"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    protocol = data.get('protocol', 'ssh')
    wordlist = data.get('wordlist', 'rockyou.txt')
    username = data.get('username', 'admin')

    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400

    if not validate_ip_address(target_ip):
        return jsonify({"error": "Invalid IP address format"}), 400

    # Validate protocol
    allowed_protocols = ['ssh', 'ftp', 'http', 'https', 'telnet', 'smtp', 'pop3', 'imap']
    if protocol not in allowed_protocols:
        return jsonify({"error": f"Unsupported protocol. Allowed: {', '.join(allowed_protocols)}"}), 400

    try:
        # Check if target is reachable first
        port_check = scan_ports(target_ip, str(get_default_port(protocol)))
        if not port_check:
            return jsonify({
                "error": f"Target port for {protocol} appears closed or unreachable",
                "target": target_ip,
                "protocol": protocol
            }), 400

        # Simulate attack phases (for demonstration - actual attacks disabled for security)
        attack_simulation = {
            "phase1": "Loading wordlist and preparing attack vectors",
            "phase2": f"Testing {protocol} service on {target_ip}:{get_default_port(protocol)}",
            "phase3": f"Attempting authentication with username: {username}",
            "phase4": "Brute force simulation (disabled for security)",
            "warning": "This is a simulation. Actual brute force attacks are disabled."
        }

        # Store detailed attack log
        attack_details = {
            "protocol": protocol,
            "target_ip": target_ip,
            "port": get_default_port(protocol),
            "username": username,
            "wordlist": wordlist,
            "simulation_phases": attack_simulation,
            "timestamp": datetime.now().isoformat(),
            "status": "simulation_completed"
        }

        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                    ("hydra_bruteforce", target_ip, "simulation_completed", json.dumps(attack_details))
                )
                conn.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")

        # Update system metrics
        system_metrics['active_scans'] += 1
        system_metrics['threats_detected'] += 1

        return jsonify({
            "status": "simulation_success",
            "message": f"Hydra brute force simulation completed against {target_ip} ({protocol})",
            "target": target_ip,
            "protocol": protocol,
            "simulation_details": attack_simulation,
            "warning": "Actual attacks are disabled for security. This was a simulation.",
            "recommendations": [
                "Use this tool only for authorized penetration testing",
                "Ensure you have written permission before testing",
                "Consider the legal implications of brute force attacks"
            ]
        })

    except Exception as e:
        return jsonify({"error": f"Hydra simulation failed: {str(e)}"}), 500

def get_default_port(protocol):
    """Get default port for protocol"""
    port_map = {
        'ssh': 22,
        'ftp': 21,
        'http': 80,
        'https': 443,
        'telnet': 23,
        'smtp': 25,
        'pop3': 110,
        'imap': 143
    }
    return port_map.get(protocol, 22)

@app.route('/api/attack/metasploit', methods=['POST'])
@require_api_key
def api_attack_metasploit():
    """Simulate Metasploit exploit execution with detailed analysis"""
    data = request.get_json() or {}
    target_ip = data.get('target_ip')
    exploit = data.get('exploit', 'generic')
    payload = data.get('payload', 'meterpreter/reverse_tcp')
    lhost = data.get('lhost', '127.0.0.1')
    lport = data.get('lport', 4444)

    if not target_ip:
        return jsonify({"error": "target_ip required"}), 400

    if not validate_ip_address(target_ip):
        return jsonify({"error": "Invalid IP address format"}), 400

    # Validate exploit name
    known_exploits = {
        'vsftpd': 'vsftpd_234_backdoor',
        'eternalblue': 'windows/smb/ms17_010_eternalblue',
        'bluekeep': 'windows/rdp/cve_2019_0708_bluekeep',
        'generic': 'multi/handler'
    }

    if exploit not in known_exploits:
        return jsonify({
            "error": f"Unknown exploit. Available: {', '.join(known_exploits.keys())}",
            "target": target_ip
        }), 400

    try:
        # Perform vulnerability assessment first
        vuln_scan = scan_ports(target_ip, "21,22,80,443,445,3389")
        open_ports = [p['port'] for p in vuln_scan]

        # Determine if exploit is applicable based on open ports
        exploit_applicable = check_exploit_compatibility(exploit, open_ports)

        if not exploit_applicable['applicable']:
            return jsonify({
                "error": f"Exploit {exploit} not applicable to target",
                "reason": exploit_applicable['reason'],
                "open_ports": open_ports,
                "target": target_ip
            }), 400

        # Simulate Metasploit execution phases
        metasploit_simulation = {
            "phase1": f"Loading exploit: {known_exploits[exploit]}",
            "phase2": f"Configuring payload: {payload}",
            "phase3": f"Setting LHOST={lhost}, LPORT={lport}",
            "phase4": f"Targeting {target_ip}",
            "phase5": "Exploit simulation (disabled for security)",
            "warning": "This is a simulation. Actual exploits are disabled."
        }

        # Detailed exploit analysis
        exploit_analysis = {
            "exploit_name": known_exploits[exploit],
            "target_ip": target_ip,
            "payload": payload,
            "lhost": lhost,
            "lport": lport,
            "vulnerability_check": exploit_applicable,
            "open_ports": open_ports,
            "simulation_phases": metasploit_simulation,
            "risk_assessment": assess_exploit_risk(exploit),
            "timestamp": datetime.now().isoformat(),
            "status": "simulation_completed"
        }

        # Store detailed attack log
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO attack_logs (attack_type, target, status, details) VALUES (?, ?, ?, ?)",
                    ("metasploit_exploit", target_ip, "simulation_completed", json.dumps(exploit_analysis))
                )
                conn.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")

        # Update system metrics
        system_metrics['active_scans'] += 1
        system_metrics['threats_detected'] += 2  # Higher threat level for exploits
        system_metrics['vulnerabilities'] += 1

        return jsonify({
            "status": "simulation_success",
            "message": f"Metasploit exploit simulation completed: {exploit} against {target_ip}",
            "target": target_ip,
            "exploit": exploit,
            "exploit_details": exploit_analysis,
            "simulation_details": metasploit_simulation,
            "warning": "Actual exploits are disabled for security. This was a simulation.",
            "recommendations": [
                "Use Metasploit only in controlled lab environments",
                "Ensure all targets are authorized for testing",
                "Consider the legal and ethical implications",
                "Document all testing activities"
            ]
        })

    except Exception as e:
        return jsonify({"error": f"Metasploit simulation failed: {str(e)}"}), 500

def check_exploit_compatibility(exploit, open_ports):
    """Check if exploit is compatible with target's open ports"""
    compatibility_map = {
        'vsftpd': {
            'required_ports': [21],
            'description': 'VSFTPD backdoor exploit requires FTP port 21'
        },
        'eternalblue': {
            'required_ports': [445],
            'description': 'EternalBlue requires SMB port 445'
        },
        'bluekeep': {
            'required_ports': [3389],
            'description': 'BlueKeep requires RDP port 3389'
        },
        'generic': {
            'required_ports': [],
            'description': 'Generic handler can work with any open port'
        }
    }

    if exploit not in compatibility_map:
        return {'applicable': False, 'reason': 'Unknown exploit'}

    required = compatibility_map[exploit]['required_ports']
    if not required:  # Generic handler
        return {'applicable': True, 'reason': compatibility_map[exploit]['description']}

    for port in required:
        if port in open_ports:
            return {'applicable': True, 'reason': compatibility_map[exploit]['description']}

    return {
        'applicable': False,
        'reason': f"{compatibility_map[exploit]['description']}. Required ports not open: {required}"
    }

def assess_exploit_risk(exploit):
    """Assess the risk level of an exploit"""
    risk_levels = {
        'vsftpd': {'level': 'high', 'cvss': 7.5, 'description': 'Remote code execution vulnerability'},
        'eternalblue': {'level': 'critical', 'cvss': 8.1, 'description': 'Wormable remote code execution'},
        'bluekeep': {'level': 'critical', 'cvss': 9.8, 'description': 'Critical RDP vulnerability'},
        'generic': {'level': 'medium', 'cvss': 5.0, 'description': 'Generic exploit handler'}
    }

    return risk_levels.get(exploit, {'level': 'unknown', 'cvss': 0.0, 'description': 'Unknown exploit'})

@app.route('/api/console/execute', methods=['POST'])
@require_api_key
def api_console_execute():
    """Execute console command (restricted for security)"""
    data = request.get_json() or {}
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({"error": "command required"}), 400
    
    # Whitelist of safe commands for demo purposes
    safe_commands = {
        'help': 'Available commands: help, status, version, time, whoami',
        'status': 'CYBER-MATRIX v8.0 - All systems operational',
        'version': 'CYBER-MATRIX v8.0 - Advanced Holographic Penetration Suite',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        'whoami': 'cyber-matrix-user'
    }
    
    # Check if command is in whitelist
    if command.lower() in safe_commands:
        output = safe_commands[command.lower()]
    else:
        # For security, don't execute arbitrary commands
        output = f"Command '{command}' not recognized. Type 'help' for available commands."
    
    return jsonify({
        "status": "success",
        "command": command,
        "output": output
    })

# ===== Network Discovery & 3D Map API Endpoints =====

@app.route('/api/networks', methods=['GET'])
def api_networks_list():
    """Get list of all discovered networks"""
    try:
        # Get networks from secure tools
        if SECURE_TOOLS_AVAILABLE:
            wifi_networks = secure_tools.get_wifi_networks_secure()
        else:
            wifi_networks = []
        
        # Get devices from database
        networks = []
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT DISTINCT ip_address, mac_address, hostname, device_type, 
                       last_seen, status, vulnerability_score
                FROM network_devices
                WHERE status = 'active'
                ORDER BY last_seen DESC
            """)
            db_devices = cursor.fetchall()
        
        # Combine WiFi networks and discovered devices
        network_id = 1
        for wifi in wifi_networks:
            networks.append({
                "id": f"wifi_{network_id}",
                "ssid": wifi.get('essid', 'Unknown'),
                "bssid": wifi.get('bssid', '00:00:00:00:00:00'),
                "mac": wifi.get('bssid', '00:00:00:00:00:00'),
                "ip": None,
                "vendor": "Unknown",
                "signal_dbm": -60,
                "rssi": wifi.get('rssi', 50),
                "channel": wifi.get('channel', 1),
                "frequency": 2400 + (wifi.get('channel', 1) * 5),
                "security": "WPA2" if wifi.get('encrypted', True) else "Open",
                "gps": None,
                "device_count": 0,
                "last_seen": datetime.now().isoformat()
            })
            network_id += 1
        
        # Add discovered devices as network nodes
        for device in db_devices:
            networks.append({
                "id": f"dev_{device['mac_address']}",
                "ssid": device['hostname'] or device['ip_address'],
                "bssid": device['mac_address'] or "00:00:00:00:00:00",
                "mac": device['mac_address'] or "00:00:00:00:00:00",
                "ip": device['ip_address'],
                "vendor": device['device_type'] or "Unknown",
                "signal_dbm": -50,
                "rssi": 70,
                "channel": 1,
                "frequency": 2412,
                "security": "Unknown",
                "gps": None,
                "device_count": 0,
                "last_seen": device['last_seen'] or datetime.now().isoformat()
            })
        
        return jsonify({
            "status": "success",
            "networks": networks,
            "total": len(networks),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Networks list error: {str(e)}")
        return jsonify({
            "status": "error",
            "networks": [],
            "total": 0,
            "error": "Failed to retrieve networks"
        }), 500

@app.route('/api/networks/<network_id>', methods=['GET'])
def api_network_detail(network_id):
    """Get details of a specific network"""
    try:
        network_id = sanitize_input(network_id, 50)
        
        # Check if it's a WiFi network or device
        if network_id.startswith('wifi_'):
            # Get from WiFi scan
            if SECURE_TOOLS_AVAILABLE:
                wifi_networks = secure_tools.get_wifi_networks_secure()
                idx = int(network_id.split('_')[1]) - 1
                if 0 <= idx < len(wifi_networks):
                    wifi = wifi_networks[idx]
                    return jsonify({
                        "status": "success",
                        "network": {
                            "id": network_id,
                            "ssid": wifi.get('essid', 'Unknown'),
                            "bssid": wifi.get('bssid', '00:00:00:00:00:00'),
                            "mac": wifi.get('bssid', '00:00:00:00:00:00'),
                            "channel": wifi.get('channel', 1),
                            "frequency": 2400 + (wifi.get('channel', 1) * 5),
                            "security": "WPA2" if wifi.get('encrypted', True) else "Open",
                            "signal_dbm": -60,
                            "last_seen": datetime.now().isoformat()
                        }
                    })
        elif network_id.startswith('dev_'):
            # Get from database
            mac = network_id.replace('dev_', '')
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM network_devices WHERE mac_address = ?",
                    (mac,)
                )
                device = cursor.fetchone()
                if device:
                    return jsonify({
                        "status": "success",
                        "network": {
                            "id": network_id,
                            "ssid": device['hostname'] or device['ip_address'],
                            "bssid": device['mac_address'],
                            "mac": device['mac_address'],
                            "ip": device['ip_address'],
                            "vendor": device['device_type'],
                            "last_seen": device['last_seen']
                        }
                    })
        
        return jsonify({"error": "Network not found"}), 404
    except Exception as e:
        app.logger.error(f"Network detail error: {str(e)}")
        return jsonify({"error": "Failed to retrieve network details"}), 500

@app.route('/api/devices', methods=['GET'])
def api_devices_list():
    """Get list of all discovered devices"""
    try:
        devices = []
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT ip_address, mac_address, hostname, device_type, 
                       last_seen, status, vulnerability_score
                FROM network_devices
                WHERE status = 'active'
                ORDER BY last_seen DESC
            """)
            db_devices = cursor.fetchall()
        
        for device in db_devices:
            devices.append({
                "id": device['mac_address'] or device['ip_address'],
                "mac": device['mac_address'] or "00:00:00:00:00:00",
                "ip": device['ip_address'],
                "hostname": device['hostname'] or "Unknown",
                "vendor": device['device_type'] or "Unknown",
                "device_type": device['device_type'] or "Unknown",
                "status": device['status'],
                "vulnerability_score": device['vulnerability_score'] or 0,
                "last_seen": device['last_seen'] or datetime.now().isoformat(),
                "signal_dbm": -50,
                "rssi": 70
            })
        
        return jsonify({
            "status": "success",
            "devices": devices,
            "total": len(devices),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Devices list error: {str(e)}")
        return jsonify({
            "status": "error",
            "devices": [],
            "total": 0,
            "error": "Failed to retrieve devices"
        }), 500

@app.route('/api/devices/<mac_address>', methods=['GET'])
def api_device_detail(mac_address):
    """Get details of a specific device"""
    try:
        mac_address = sanitize_input(mac_address, 20)
        
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM network_devices WHERE mac_address = ?",
                (mac_address,)
            )
            device = cursor.fetchone()
        
        if device:
            return jsonify({
                "status": "success",
                "device": {
                    "id": device['mac_address'],
                    "mac": device['mac_address'],
                    "ip": device['ip_address'],
                    "hostname": device['hostname'] or "Unknown",
                    "vendor": device['device_type'],
                    "device_type": device['device_type'],
                    "status": device['status'],
                    "vulnerability_score": device['vulnerability_score'],
                    "last_seen": device['last_seen']
                }
            })
        else:
            return jsonify({"error": "Device not found"}), 404
    except Exception as e:
        app.logger.error(f"Device detail error: {str(e)}")
        return jsonify({"error": "Failed to retrieve device details"}), 500

# ===== WebSocket Handlers =====

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    app.logger.info("WebSocket client connected")
    emit('connected', {'status': 'connected', 'message': 'Connected to CYBER-MATRIX'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    app.logger.info("WebSocket client disconnected")

@socketio.on('subscribe_networks')
def handle_subscribe_networks():
    """Subscribe to network updates"""
    app.logger.info("Client subscribed to network updates")
    emit('subscribed', {'status': 'subscribed', 'channel': 'networks'})

def broadcast_network_update(update_type, network_data):
    """Broadcast network update to all connected clients"""
    try:
        socketio.emit('network_update', {
            'type': update_type,
            'data': network_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"WebSocket broadcast error: {str(e)}")

def network_monitor_thread():
    """Background thread to monitor and broadcast network changes"""
    last_networks = []
    while True:
        try:
            time.sleep(10)  # Poll every 10 seconds
            
            # Get current networks
            networks = []
            if SECURE_TOOLS_AVAILABLE:
                wifi_networks = secure_tools.get_wifi_networks_secure()
                network_id = 1
                for wifi in wifi_networks:
                    networks.append({
                        "id": f"wifi_{network_id}",
                        "ssid": wifi.get('essid', 'Unknown'),
                        "bssid": wifi.get('bssid', '00:00:00:00:00:00'),
                        "mac": wifi.get('bssid', '00:00:00:00:00:00'),
                        "signal_dbm": -60,
                        "channel": wifi.get('channel', 1),
                        "security": "WPA2" if wifi.get('encrypted', True) else "Open",
                        "last_seen": datetime.now().isoformat()
                    })
                    network_id += 1
            
            # Get devices from database
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT ip_address, mac_address, hostname, device_type, last_seen
                    FROM network_devices
                    WHERE status = 'active'
                    ORDER BY last_seen DESC
                """)
                db_devices = cursor.fetchall()
            
            for device in db_devices:
                networks.append({
                    "id": f"dev_{device['mac_address']}",
                    "ssid": device['hostname'] or device['ip_address'],
                    "bssid": device['mac_address'],
                    "mac": device['mac_address'],
                    "ip": device['ip_address'],
                    "vendor": device['device_type'],
                    "last_seen": device['last_seen']
                })
            
            # Check for changes
            current_ids = set(n['id'] for n in networks)
            last_ids = set(n['id'] for n in last_networks)
            
            # New networks
            new_ids = current_ids - last_ids
            for network in networks:
                if network['id'] in new_ids:
                    broadcast_network_update('add', network)
            
            # Removed networks
            removed_ids = last_ids - current_ids
            for network in last_networks:
                if network['id'] in removed_ids:
                    broadcast_network_update('remove', network)
            
            # Updated networks
            for network in networks:
                if network['id'] in last_ids:
                    broadcast_network_update('update', network)
            
            last_networks = networks
            
        except Exception as e:
            app.logger.error(f"Network monitor thread error: {str(e)}")
            time.sleep(30)

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
    
    # Start network monitor thread
    network_thread = threading.Thread(target=network_monitor_thread, daemon=True)
    network_thread.start()
    
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
    print("🌐 Dashboard will be available at: http://127.0.0.1:5001")
    print("🔒 API endpoints active and ready")
    print("⚡ Real-time metrics enabled")
    print("🔌 WebSocket server active at ws://127.0.0.1:5001/socket.io/")
    
    # Run the Flask app with SocketIO
    host = os.environ.get('CYBER_MATRIX_HOST', '127.0.0.1')
    port = int(os.environ.get('CYBER_MATRIX_PORT', '5001'))
    
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
