#!/usr/bin/env python3
"""
Web-compatible Network Interface Manager
Converted from Tkinter to Flask API backend for CYBER-MATRIX integration.

A sophisticated network interface management component with monitor mode capabilities.
Designed for seamless integration into larger network security tooling.
"""

import subprocess
import re
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class NetworkInterfaceManager:
    """
    A sophisticated network interface management component with monitor mode capabilities.
    Web-compatible version for Flask integration.
    """
    
    def __init__(self):
        """Initialize the network interface manager."""
        self.interfaces = {}
        self.refresh_lock = threading.Lock()
        self.is_refreshing = False
        self.last_refresh = None
        
        # Auto-refresh on initialization
        self._refresh_interfaces()
    
    def _execute_command(self, cmd: List[str], require_root: bool = False, timeout: int = 10) -> Tuple[bool, str, str]:
        """
        Execute a system command with appropriate privilege escalation.
        
        Args:
            cmd: Command list
            require_root: Whether root privileges are required
            timeout: Command timeout in seconds
            
        Returns:
            tuple: (success, output, error)
        """
        try:
            # Check if we need root and don't have it
            if require_root:
                try:
                    uid_result = subprocess.run(['id', '-u'], capture_output=True, text=True, timeout=5)
                    if uid_result.returncode == 0 and uid_result.stdout.strip() != '0':
                        # Attempt privilege escalation
                        cmd = ['sudo'] + cmd
                except:
                    # If we can't check, assume we need sudo
                    cmd = ['sudo'] + cmd
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
    
    def _get_interfaces(self) -> Dict[str, Any]:
        """
        Enumerate all network interfaces with their current states.
        Enhanced to detect both wireless and wired interfaces with fallback to psutil.
        
        Returns:
            dict: Interface data keyed by interface name
        """
        interfaces = {}
        
        # Try system commands first, fallback to psutil
        success, output, error = self._execute_command(['ip', 'link', 'show'])
        if success:
            # Parse ip link output
            interfaces = self._parse_ip_link_output(output)
        else:
            # Fallback to psutil-based detection
            print(f"ip command not available ({error}), using psutil fallback")
            interfaces = self._get_interfaces_psutil()
        
        return interfaces
    
    def _parse_ip_link_output(self, output: str) -> Dict[str, Any]:
        """Parse ip link show output."""
        interfaces = {}
        
        for line in output.split('\n'):
            # Match interface line (e.g., "2: wlan0: <BROADCAST,MULTICAST,UP>")
            iface_match = re.match(r'^\d+:\s+(\w+):\s+<([^>]+)>', line)
            if iface_match:
                iface_name = iface_match.group(1)
                flags = iface_match.group(2)
                
                # Skip loopback
                if iface_name == 'lo':
                    continue
                
                # Determine if interface is up
                is_up = 'UP' in flags
                
                # Get IP addresses
                ipv4, ipv6, mac = self._get_interface_addresses(iface_name)
                
                # Check if it's a wireless interface
                is_wireless, current_mode, monitor_supported = self._check_wireless_capabilities(iface_name)
                
                # Determine interface type
                if is_wireless:
                    iface_type = 'wireless'
                elif iface_name.startswith(('eth', 'en')):
                    iface_type = 'ethernet'
                elif iface_name.startswith('docker'):
                    iface_type = 'bridge'
                else:
                    iface_type = 'other'
                
                interfaces[iface_name] = {
                    'name': iface_name,
                    'is_up': is_up,
                    'is_wireless': is_wireless,
                    'type': iface_type,
                    'mode': current_mode,
                    'is_monitor': current_mode.lower() == 'monitor' if current_mode else False,
                    'monitor_supported': monitor_supported,
                    'flags': flags,
                    'ipv4': ipv4,
                    'ipv6': ipv6,
                    'mac': mac,
                    'last_updated': datetime.now().isoformat()
                }
        
        return interfaces
    
    def _get_interfaces_psutil(self) -> Dict[str, Any]:
        """Fallback method using psutil when system commands aren't available."""
        interfaces = {}
        
        try:
            import psutil
            import socket
            
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            for name, stat in stats.items():
                # Skip loopback
                if name == 'lo':
                    continue
                
                iface_addrs = addrs.get(name, [])
                ipv4 = ""
                ipv6 = ""
                mac = ""
                
                for addr in iface_addrs:
                    fam = getattr(addr, 'family', None)
                    if fam == socket.AF_PACKET and not mac:  # MAC address
                        mac = addr.address
                    elif fam == socket.AF_INET and not ipv4:  # IPv4
                        ipv4 = addr.address
                    elif fam == socket.AF_INET6 and not ipv6:  # IPv6
                        ipv6 = addr.address
                
                # Determine interface type
                lowered = name.lower()
                if lowered.startswith(('wl', 'wlan')):
                    iface_type = 'wireless'
                    is_wireless = True
                elif lowered.startswith(('eth', 'en')):
                    iface_type = 'ethernet'
                    is_wireless = False
                elif lowered.startswith('docker'):
                    iface_type = 'bridge'
                    is_wireless = False
                else:
                    iface_type = 'other'
                    is_wireless = False
                
                # For wireless interfaces, try to get mode info
                current_mode = 'Managed'
                monitor_supported = False
                is_monitor = False
                
                if is_wireless:
                    # Try to get wireless info
                    is_wireless, current_mode, monitor_supported = self._check_wireless_capabilities(name)
                    is_monitor = current_mode.lower() == 'monitor' if current_mode else False
                
                interfaces[name] = {
                    'name': name,
                    'is_up': bool(getattr(stat, 'isup', False)),
                    'is_wireless': is_wireless,
                    'type': iface_type,
                    'mode': current_mode,
                    'is_monitor': is_monitor,
                    'monitor_supported': monitor_supported,
                    'flags': 'UP' if getattr(stat, 'isup', False) else 'DOWN',
                    'ipv4': ipv4,
                    'ipv6': ipv6,
                    'mac': mac,
                    'mtu': getattr(stat, 'mtu', None),
                    'last_updated': datetime.now().isoformat()
                }
        
        except ImportError:
            print("psutil not available for interface detection")
        except Exception as e:
            print(f"Error in psutil interface detection: {e}")
        
        return interfaces
    
    def _get_interface_addresses(self, iface_name: str) -> Tuple[str, str, str]:
        """Get IP and MAC addresses for an interface."""
        ipv4 = ""
        ipv6 = ""
        mac = ""
        
        # Get IP addresses
        success, output, _ = self._execute_command(['ip', 'addr', 'show', iface_name])
        if success:
            # Parse IPv4
            ipv4_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', output)
            if ipv4_match:
                ipv4 = ipv4_match.group(1)
            
            # Parse IPv6
            ipv6_match = re.search(r'inet6 ([a-fA-F0-9:]+)', output)
            if ipv6_match:
                ipv6 = ipv6_match.group(1)
            
            # Parse MAC address
            mac_match = re.search(r'link/ether ([a-fA-F0-9:]{17})', output)
            if mac_match:
                mac = mac_match.group(1)
        
        return ipv4, ipv6, mac
    
    def _check_wireless_capabilities(self, iface_name: str) -> Tuple[bool, str, bool]:
        """
        Check if interface is wireless and get its capabilities.
        
        Returns:
            tuple: (is_wireless, current_mode, monitor_supported)
        """
        # Check with iwconfig first
        success, iwconfig_out, _ = self._execute_command(['iwconfig', iface_name])
        if success and 'no wireless extensions' not in iwconfig_out.lower():
            # It's a wireless interface
            mode_match = re.search(r'Mode:(\w+)', iwconfig_out)
            current_mode = mode_match.group(1) if mode_match else 'Managed'
            
            # Check if monitor mode is supported
            monitor_supported = self._check_monitor_support(iface_name)
            
            return True, current_mode, monitor_supported
        
        # Check with iw as fallback
        success, iw_out, _ = self._execute_command(['iw', 'dev', iface_name, 'info'])
        if success:
            # Parse iw output for mode
            mode_match = re.search(r'type (\w+)', iw_out)
            current_mode = mode_match.group(1) if mode_match else 'managed'
            
            # Check monitor support
            monitor_supported = self._check_monitor_support(iface_name)
            
            return True, current_mode.capitalize(), monitor_supported
        
        return False, 'N/A', False
    
    def _check_monitor_support(self, iface_name: str) -> bool:
        """Check if interface supports monitor mode."""
        # Check with iw list for supported modes
        success, output, _ = self._execute_command(['iw', 'phy'])
        if success and 'monitor' in output.lower():
            return True
        
        # Fallback: assume modern wireless interfaces support monitor mode
        success, output, _ = self._execute_command(['iwconfig', iface_name])
        return success and 'no wireless extensions' not in output.lower()
    
    def refresh_interfaces(self) -> Dict[str, Any]:
        """
        Refresh the interface list.
        Thread-safe method for web API calls.
        
        Returns:
            dict: Updated interface data
        """
        if self.is_refreshing:
            return self.interfaces
        
        with self.refresh_lock:
            self.is_refreshing = True
            try:
                self.interfaces = self._get_interfaces()
                self.last_refresh = datetime.now()
            finally:
                self.is_refreshing = False
        
        return self.interfaces
    
    def _refresh_interfaces(self):
        """Internal refresh method."""
        self.refresh_interfaces()
    
    def get_interface_data(self, iface_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed data for an interface.
        
        Args:
            iface_name: Interface name
            
        Returns:
            dict or None: Interface data or None if not found
        """
        if iface_name is None:
            return None
        
        return self.interfaces.get(iface_name)
    
    def get_all_interfaces(self) -> Dict[str, Any]:
        """Get all interface data."""
        return self.interfaces
    
    def toggle_monitor_mode(self, iface_name: str, enable: bool) -> Tuple[bool, str]:
        """
        Toggle monitor mode for the specified interface.
        
        Args:
            iface_name: Interface name
            enable: True to enable monitor mode, False to disable
            
        Returns:
            tuple: (success, error_message)
        """
        if iface_name not in self.interfaces:
            return False, f"Interface {iface_name} not found"
        
        iface_data = self.interfaces[iface_name]
        
        if not iface_data['is_wireless']:
            return False, f"Interface {iface_name} is not wireless"
        
        if not iface_data['monitor_supported']:
            return False, f"Interface {iface_name} does not support monitor mode"
        
        try:
            if enable:
                success, error_msg = self._enable_monitor_mode(iface_name)
            else:
                success, error_msg = self._disable_monitor_mode(iface_name)
            
            if success:
                # Refresh interface state
                time.sleep(0.5)
                self._refresh_interfaces()
            
            return success, error_msg
        except Exception as e:
            return False, str(e)
    
    def _enable_monitor_mode(self, iface_name: str) -> Tuple[bool, str]:
        """Enable monitor mode on the specified interface."""
        # Take interface down
        success, _, error = self._execute_command(['ip', 'link', 'set', iface_name, 'down'], require_root=True)
        if not success:
            return False, f"Failed to bring interface down: {error}"
        
        # Set monitor mode using iw (preferred) or iwconfig (fallback)
        success, _, error = self._execute_command(['iw', 'dev', iface_name, 'set', 'type', 'monitor'], require_root=True)
        if not success:
            # Fallback to iwconfig
            success, _, error = self._execute_command(['iwconfig', iface_name, 'mode', 'monitor'], require_root=True)
            if not success:
                return False, f"Failed to set monitor mode: {error}"
        
        # Bring interface back up
        success, _, error = self._execute_command(['ip', 'link', 'set', iface_name, 'up'], require_root=True)
        if not success:
            return False, f"Failed to bring interface up: {error}"
        
        return True, ""
    
    def _disable_monitor_mode(self, iface_name: str) -> Tuple[bool, str]:
        """Disable monitor mode on the specified interface."""
        # Take interface down
        success, _, error = self._execute_command(['ip', 'link', 'set', iface_name, 'down'], require_root=True)
        if not success:
            return False, f"Failed to bring interface down: {error}"
        
        # Set managed mode
        success, _, error = self._execute_command(['iw', 'dev', iface_name, 'set', 'type', 'managed'], require_root=True)
        if not success:
            # Fallback to iwconfig
            success, _, error = self._execute_command(['iwconfig', iface_name, 'mode', 'managed'], require_root=True)
            if not success:
                return False, f"Failed to set managed mode: {error}"
        
        # Bring interface back up
        success, _, error = self._execute_command(['ip', 'link', 'set', iface_name, 'up'], require_root=True)
        if not success:
            return False, f"Failed to bring interface up: {error}"
        
        return True, ""
    
    def get_interface_status_summary(self) -> Dict[str, Any]:
        """Get a summary of interface statuses for dashboard display."""
        summary = {
            'total_interfaces': len(self.interfaces),
            'wireless_interfaces': 0,
            'interfaces_up': 0,
            'monitor_mode_active': 0,
            'monitor_capable': 0,
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None
        }
        
        for iface_data in self.interfaces.values():
            if iface_data['is_wireless']:
                summary['wireless_interfaces'] += 1
            if iface_data['is_up']:
                summary['interfaces_up'] += 1
            if iface_data['is_monitor']:
                summary['monitor_mode_active'] += 1
            if iface_data['monitor_supported']:
                summary['monitor_capable'] += 1
        
        return summary


# Global instance for Flask integration
network_manager = NetworkInterfaceManager()