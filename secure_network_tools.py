#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Secure Network Tools Module
Replacement for vulnerable kamkrk_v2.py, detect.py, and networks.py

This module provides secure implementations of network discovery and security tools
with proper input validation, sanitization, and command injection prevention.
"""

import subprocess
import re
import os
import json
import time
import socket
import ipaddress
import logging
import shlex
from typing import List, Dict, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class SecureNetworkTools:
    """Secure network tools with input validation and safe command execution"""
    
    def __init__(self):
        self.allowed_commands = {
            'ping': ['/bin/ping', '/usr/bin/ping'],
            'nmap': ['/usr/bin/nmap', '/bin/nmap'],
            'arp': ['/usr/sbin/arp', '/sbin/arp'],
            'iwlist': ['/sbin/iwlist', '/usr/sbin/iwlist'],
            'netstat': ['/bin/netstat', '/usr/bin/netstat'],
            'ps': ['/bin/ps', '/usr/bin/ps']
        }
    
    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _validate_cidr_range(self, cidr: str) -> bool:
        """Validate CIDR notation"""
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False
    
    def _sanitize_input(self, input_str: str, max_length: int = 100) -> str:
        """Sanitize user input"""
        if not isinstance(input_str, str):
            return ""
        # Remove dangerous characters
        sanitized = re.sub(r'[;&|`$(){}\\[\\]<>"\']', '', input_str)
        return sanitized[:max_length].strip()
    
    def _find_command_path(self, command: str) -> Optional[str]:
        """Find the full path of a command"""
        if command not in self.allowed_commands:
            return None
        
        for path in self.allowed_commands[command]:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Fallback to which command
        try:
            result = subprocess.run(['which', command], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def _run_secure_command(self, command_list: List[str], timeout: int = 30) -> tuple:
        """Execute commands securely without shell=True"""
        try:
            # Validate command
            if not command_list or not isinstance(command_list, list):
                return None, "Invalid command format"
            
            cmd_name = os.path.basename(command_list[0])
            if cmd_name not in self.allowed_commands:
                return None, f"Command not allowed: {cmd_name}"
            
            # Find full command path
            cmd_path = self._find_command_path(cmd_name)
            if not cmd_path:
                return None, f"Command not found: {cmd_name}"
            
            # Replace command with full path
            command_list[0] = cmd_path
            
            # Execute with strict security
            result = subprocess.run(
                command_list,
                shell=False,  # Never use shell=True
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Don't raise on non-zero exit
            )
            
            return result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return None, "Command timed out"
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return None, "Command execution failed"
    
    def discover_network_devices(self, ip_range: str = "192.168.1.0/24") -> List[Dict]:
        """Discover devices on the network safely"""
        devices = []
        
        try:
            # Validate IP range
            ip_range = self._sanitize_input(ip_range, 20)
            if not self._validate_cidr_range(ip_range):
                logger.warning(f"Invalid IP range: {ip_range}")
                return []
            
            # Method 1: ARP table
            stdout, stderr = self._run_secure_command(['arp', '-a'])
            if stdout:
                for line in stdout.splitlines():
                    match = re.search(r'\(([\d.]+)\) at ([a-fA-F0-9:]+)', line)
                    if match:
                        ip, mac = match.groups()
                        if self._validate_ip_address(ip):
                            try:
                                hostname = socket.gethostbyaddr(ip)[0]
                            except:
                                hostname = "Unknown"
                            
                            devices.append({
                                "ip": ip,
                                "mac": mac,
                                "hostname": self._sanitize_input(hostname, 50),
                                "method": "ARP",
                                "status": "active"
                            })
            
            # Method 2: Limited ping sweep
            if not devices:
                try:
                    network = ipaddress.IPv4Network(ip_range, strict=False)
                    # Limit to first 5 IPs for safety
                    for ip in list(network.hosts())[:5]:
                        stdout, stderr = self._run_secure_command([
                            'ping', '-c', '1', '-W', '2', str(ip)
                        ])
                        if stdout and '1 received' in stdout:
                            devices.append({
                                "ip": str(ip),
                                "mac": "Unknown",
                                "hostname": "Unknown",
                                "method": "Ping",
                                "status": "active"
                            })
                except Exception as e:
                    logger.error(f"Ping sweep error: {str(e)}")
            
            logger.info(f"Network discovery completed: {len(devices)} devices found")
            return devices
            
        except Exception as e:
            logger.error(f"Network discovery error: {str(e)}")
            return []
    
    def scan_ports_secure(self, target_ip: str, port_range: str = "22,80,443") -> List[Dict]:
        """Scan ports securely with limited scope"""
        try:
            # Validate inputs
            target_ip = self._sanitize_input(target_ip, 15)
            if not self._validate_ip_address(target_ip):
                logger.warning(f"Invalid IP address: {target_ip}")
                return []
            
            port_range = self._sanitize_input(port_range, 50)
            
            # Use nmap with very restricted options
            stdout, stderr = self._run_secure_command([
                'nmap', '-p', port_range, '-T2', '--max-retries', '1', 
                '--host-timeout', '30s', target_ip
            ])
            
            open_ports = []
            if stdout:
                for line in stdout.splitlines():
                    if '/tcp' in line and 'open' in line:
                        try:
                            port_str = line.split('/')[0].strip()
                            port = int(port_str)
                            if 1 <= port <= 65535:
                                service_parts = line.split()
                                service = service_parts[-1] if len(service_parts) > 2 else "unknown"
                                open_ports.append({
                                    "port": port,
                                    "service": self._sanitize_input(service, 20),
                                    "state": "open"
                                })
                        except (ValueError, IndexError):
                            continue
            
            logger.info(f"Port scan completed for {target_ip}: {len(open_ports)} open ports")
            return open_ports
            
        except Exception as e:
            logger.error(f"Port scan error: {str(e)}")
            return []
    
    def get_local_network_info(self) -> Dict:
        """Get local network information safely"""
        try:
            info = {}
            
            # Get local IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                info['local_ip'] = s.getsockname()[0]
                s.close()
            except:
                info['local_ip'] = "Unknown"
            
            # Get hostname
            try:
                info['hostname'] = socket.gethostname()
            except:
                info['hostname'] = "Unknown"
            
            return info
            
        except Exception as e:
            logger.error(f"Network info error: {str(e)}")
            return {"error": "Failed to get network info"}
    
    def get_wifi_networks_secure(self) -> List[Dict]:
        """Get WiFi networks with security validation"""
        networks = []
        
        try:
            # Try iwlist scan with timeout
            stdout, stderr = self._run_secure_command(['iwlist', 'scan'], timeout=15)
            if stdout:
                current_network = {}
                for line in stdout.splitlines():
                    line = line.strip()
                    if "Cell" in line:
                        if current_network:
                            networks.append(current_network)
                        current_network = {}
                    elif "Address:" in line and "Address: " in line:
                        address = line.split("Address: ")[1].strip()
                        current_network["bssid"] = self._sanitize_input(address, 20)
                    elif "ESSID:" in line and "ESSID:" in line:
                        essid_part = line.split("ESSID:")[1].strip().strip('"')
                        if essid_part and essid_part != "<hidden>":
                            current_network["essid"] = self._sanitize_input(essid_part, 50)
                    elif "Channel:" in line and "Channel:" in line:
                        channel = line.split("Channel:")[1].strip()
                        try:
                            channel_num = int(channel)
                            if 1 <= channel_num <= 165:
                                current_network["channel"] = channel_num
                        except ValueError:
                            pass
                    elif "Encryption key:" in line:
                        current_network["encrypted"] = "on" in line.lower()
                
                if current_network:
                    networks.append(current_network)
        
        except Exception as e:
            logger.error(f"WiFi scan error: {str(e)}")
        
        return networks[:10]  # Limit results
    
    def simulate_security_test(self, target_ip: str, test_type: str) -> Dict:
        """Simulate security tests for educational purposes"""
        try:
            target_ip = self._sanitize_input(target_ip, 15)
            test_type = self._sanitize_input(test_type, 20)
            
            if not self._validate_ip_address(target_ip):
                return {"error": "Invalid IP address"}
            
            # Simulation responses for educational purposes
            simulation_results = {
                "ssh_test": {
                    "status": "simulated",
                    "message": f"SSH security test simulation for {target_ip}",
                    "findings": ["SSH service detected", "Key-based auth recommended"],
                    "severity": "low"
                },
                "http_test": {
                    "status": "simulated", 
                    "message": f"HTTP security test simulation for {target_ip}",
                    "findings": ["HTTP service detected", "HTTPS upgrade recommended"],
                    "severity": "medium"
                },
                "general": {
                    "status": "simulated",
                    "message": f"General security test simulation for {target_ip}",
                    "findings": ["Educational simulation completed"],
                    "severity": "info"
                }
            }
            
            result = simulation_results.get(test_type, simulation_results["general"])
            result["target"] = target_ip
            result["timestamp"] = time.time()
            result["note"] = "This is a simulation for educational purposes only"
            
            logger.info(f"Security test simulation: {test_type} for {target_ip}")
            return result
            
        except Exception as e:
            logger.error(f"Security test simulation error: {str(e)}")
            return {"error": "Simulation failed"}

# Global instance for use by the main application
secure_tools = SecureNetworkTools()