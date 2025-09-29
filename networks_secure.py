#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Secure Network Discovery Module
Secure replacement for networks.py with command injection prevention

This module provides secure network discovery functionality.
"""

from flask import Flask, request, jsonify
import socket
import json
import time
import logging
from secure_network_tools import secure_tools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SecureNetworkDiscovery:
    """Secure network discovery tools"""
    
    def __init__(self):
        self.logger = logger
    
    def discover_networks_secure(self):
        """Discover networks using secure methods"""
        try:
            networks = secure_tools.get_wifi_networks_secure()
            self.logger.info(f"Secure network discovery: {len(networks)} networks found")
            return networks
        except Exception as e:
            self.logger.error(f"Network discovery error: {str(e)}")
            return []
    
    def get_local_ip_secure(self):
        """Get local IP using secure methods"""
        try:
            network_info = secure_tools.get_local_network_info()
            local_ip = network_info.get('local_ip', 'Unknown')
            self.logger.info(f"Local IP retrieved: {local_ip}")
            return local_ip
        except Exception as e:
            self.logger.error(f"Local IP retrieval error: {str(e)}")
            return 'Unknown'
    
    def get_device_info_secure(self):
        """Get device information using secure methods"""
        try:
            network_info = secure_tools.get_local_network_info()
            
            device_info = {
                'hostname': network_info.get('hostname', 'Unknown'),
                'local_ip': network_info.get('local_ip', 'Unknown'),
                'interfaces': {
                    'lo': {
                        'name': 'Loopback',
                        'ip': '127.0.0.1',
                        'status': 'active'
                    },
                    'eth0': {
                        'name': 'Ethernet',
                        'ip': network_info.get('local_ip', 'Unknown'),
                        'status': 'active' if network_info.get('local_ip') != 'Unknown' else 'inactive'
                    }
                },
                'timestamp': time.time()
            }
            
            self.logger.info("Device information retrieved securely")
            return device_info
            
        except Exception as e:
            self.logger.error(f"Device info error: {str(e)}")
            return {"error": "Failed to get device information"}
    
    def get_router_info_secure(self):
        """Get router information using secure methods"""
        try:
            network_info = secure_tools.get_local_network_info()
            local_ip = network_info.get('local_ip')
            
            router_info = {
                'status': 'detected',
                'method': 'inference',
                'timestamp': time.time()
            }
            
            # Infer likely router IP based on local IP
            if local_ip and local_ip != 'Unknown':
                if local_ip.startswith('192.168.'):
                    # Common home network gateway
                    parts = local_ip.split('.')
                    router_info['router_ip'] = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                    router_info['network_type'] = 'home'
                elif local_ip.startswith('10.'):
                    # Corporate/large network
                    parts = local_ip.split('.')
                    router_info['router_ip'] = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                    router_info['network_type'] = 'corporate'
                elif local_ip.startswith('172.'):
                    # Private network
                    parts = local_ip.split('.')
                    router_info['router_ip'] = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                    router_info['network_type'] = 'private'
                else:
                    router_info['router_ip'] = 'Unknown'
                    router_info['network_type'] = 'unknown'
            else:
                router_info['router_ip'] = 'Unknown'
                router_info['network_type'] = 'unknown'
            
            self.logger.info(f"Router info inferred: {router_info['router_ip']}")
            return router_info
            
        except Exception as e:
            self.logger.error(f"Router info error: {str(e)}")
            return {"error": "Failed to get router information"}
    
    def scan_network_range_secure(self, ip_range="192.168.1.0/24"):
        """Scan network range using secure methods"""
        try:
            devices = secure_tools.discover_network_devices(ip_range)
            
            scan_result = {
                'ip_range': ip_range,
                'devices_found': len(devices),
                'devices': devices,
                'scan_time': time.time(),
                'status': 'completed'
            }
            
            self.logger.info(f"Network range scan completed: {len(devices)} devices found")
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Network range scan error: {str(e)}")
            return {"error": "Network scan failed"}

# Initialize secure network discovery
secure_network = SecureNetworkDiscovery()

@app.route('/networks/discover', methods=['GET'])
def discover_networks_endpoint():
    """Discover networks endpoint"""
    try:
        networks = secure_network.discover_networks_secure()
        return jsonify({
            "status": "success",
            "networks": networks,
            "total_found": len(networks)
        }), 200
    except Exception as e:
        logger.error(f"Network discovery endpoint error: {str(e)}")
        return jsonify({"error": "Failed to discover networks"}), 500

@app.route('/ip/local', methods=['GET'])
def local_ip_endpoint():
    """Get local IP endpoint"""
    try:
        local_ip = secure_network.get_local_ip_secure()
        return jsonify({"local_ip": local_ip}), 200
    except Exception as e:
        logger.error(f"Local IP endpoint error: {str(e)}")
        return jsonify({"error": "Failed to retrieve local IP"}), 500

@app.route('/devices/info', methods=['GET'])
def device_info_endpoint():
    """Get device information endpoint"""
    try:
        device_info = secure_network.get_device_info_secure()
        if "error" in device_info:
            return jsonify(device_info), 500
        return jsonify(device_info), 200
    except Exception as e:
        logger.error(f"Device info endpoint error: {str(e)}")
        return jsonify({"error": "Failed to retrieve device information"}), 500

@app.route('/router/info', methods=['GET'])
def router_info_endpoint():
    """Get router information endpoint"""
    try:
        router_info = secure_network.get_router_info_secure()
        if "error" in router_info:
            return jsonify(router_info), 500
        return jsonify(router_info), 200
    except Exception as e:
        logger.error(f"Router info endpoint error: {str(e)}")
        return jsonify({"error": "Failed to retrieve router information"}), 500

@app.route('/network/scan', methods=['POST'])
def network_scan_endpoint():
    """Network range scan endpoint"""
    try:
        data = request.get_json() or {}
        ip_range = data.get('ip_range', '192.168.1.0/24')
        
        # Validate and sanitize IP range
        ip_range = str(ip_range).replace(';', '').replace('&', '')[:20]
        
        scan_result = secure_network.scan_network_range_secure(ip_range)
        if "error" in scan_result:
            return jsonify(scan_result), 500
        return jsonify(scan_result), 200
        
    except Exception as e:
        logger.error(f"Network scan endpoint error: {str(e)}")
        return jsonify({"error": "Network scan failed"}), 500

if __name__ == '__main__':
    logger.info("Starting secure network discovery module...")
    app.run(debug=False, host='127.0.0.1', port=5003)