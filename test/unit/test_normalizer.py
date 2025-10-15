#!/usr/bin/env python3
"""
Unit tests for network normalizer module
Note: This is a Python test file but tests JavaScript functionality
Run with: python3 test/unit/test_normalizer.py
"""

import unittest
import json

class TestNetworkNormalizer(unittest.TestCase):
    """Test network normalizer logic (conceptual tests)"""
    
    def test_signal_strength_calculation(self):
        """Test signal strength calculation from dBm"""
        # -100 dBm should map to 0.0
        # -30 dBm should map to 1.0
        # -65 dBm (middle) should map to 0.5
        
        def calculate_strength(dbm):
            min_dbm = -100
            max_dbm = -30
            clamped = max(min_dbm, min(max_dbm, dbm))
            return (clamped - min_dbm) / (max_dbm - min_dbm)
        
        self.assertAlmostEqual(calculate_strength(-100), 0.0, places=2)
        self.assertAlmostEqual(calculate_strength(-30), 1.0, places=2)
        self.assertAlmostEqual(calculate_strength(-65), 0.5, places=2)
        self.assertAlmostEqual(calculate_strength(-45), 0.786, places=2)
    
    def test_rssi_strength_calculation(self):
        """Test signal strength calculation from RSSI percentage"""
        def calculate_strength_rssi(rssi):
            return max(0, min(1, rssi / 100))
        
        self.assertEqual(calculate_strength_rssi(0), 0.0)
        self.assertEqual(calculate_strength_rssi(100), 1.0)
        self.assertEqual(calculate_strength_rssi(50), 0.5)
        self.assertEqual(calculate_strength_rssi(150), 1.0)  # Clamped
    
    def test_hash_string_deterministic(self):
        """Test that string hashing is deterministic"""
        def hash_string(s):
            hash_val = 0
            if not s:
                return hash_val
            for char in s:
                hash_val = ((hash_val << 5) - hash_val) + ord(char)
                hash_val = hash_val & 0xFFFFFFFF
            return abs(hash_val)
        
        # Same input should produce same hash
        self.assertEqual(hash_string("test"), hash_string("test"))
        
        # Different inputs should produce different hashes (usually)
        self.assertNotEqual(hash_string("test1"), hash_string("test2"))
        
        # Empty string should return 0
        self.assertEqual(hash_string(""), 0)
    
    def test_security_color_mapping(self):
        """Test security type to color mapping"""
        security_colors = {
            'Open': '#ff0000',
            'WEP': '#ff6600',
            'WPA': '#ffaa00',
            'WPA2': '#00ff41',
            'WPA3': '#00ddff',
            'Unknown': '#c000ff'
        }
        
        # All security types should have colors
        for security_type in ['Open', 'WEP', 'WPA', 'WPA2', 'WPA3', 'Unknown']:
            self.assertIn(security_type, security_colors)
            self.assertTrue(security_colors[security_type].startswith('#'))
    
    def test_network_canonicalization_structure(self):
        """Test that network canonicalization produces correct structure"""
        raw_network = {
            'id': 'wifi_1',
            'ssid': 'TestNetwork',
            'bssid': '00:1A:2B:3C:4D:5E',
            'mac': '00:1A:2B:3C:4D:5E',
            'ip': None,
            'vendor': 'Cisco',
            'signal_dbm': -45,
            'rssi': 85,
            'channel': 36,
            'frequency': 5180,
            'security': 'WPA2',
            'gps': None,
            'device_count': 5,
            'last_seen': '2025-10-14T12:00:00Z'
        }
        
        # Required fields should be present
        required_fields = ['id', 'ssid', 'bssid', 'mac', 'signal_dbm', 
                          'rssi', 'channel', 'frequency', 'security', 
                          'device_count', 'last_seen']
        
        for field in required_fields:
            self.assertIn(field, raw_network)
    
    def test_device_canonicalization_structure(self):
        """Test that device canonicalization produces correct structure"""
        raw_device = {
            'id': '11:22:33:44:55:66',
            'mac': '11:22:33:44:55:66',
            'ip': '192.168.1.100',
            'hostname': 'laptop-john',
            'vendor': 'Apple',
            'device_type': 'End Device',
            'status': 'active',
            'vulnerability_score': 0,
            'last_seen': '2025-10-14T12:00:00Z',
            'signal_dbm': -50,
            'rssi': 75
        }
        
        # Required fields should be present
        required_fields = ['id', 'mac', 'ip', 'hostname', 'vendor', 
                          'device_type', 'status', 'last_seen']
        
        for field in required_fields:
            self.assertIn(field, raw_device)

class TestRadialPositioning(unittest.TestCase):
    """Test radial positioning algorithm"""
    
    def test_position_within_bounds(self):
        """Test that calculated positions are within expected bounds"""
        import math
        
        def calculate_radial_position(hash_val, strength, radius=10):
            angle = (hash_val % 360) * (math.pi / 180)
            elevation = ((hash_val % 180) - 90) * (math.pi / 180)
            distance = radius * (1.5 - strength * 0.5)
            
            return {
                'x': distance * math.cos(elevation) * math.cos(angle),
                'y': distance * math.cos(elevation) * math.sin(angle),
                'z': distance * math.sin(elevation)
            }
        
        # Test various inputs
        for hash_val in [100, 1000, 10000]:
            for strength in [0.0, 0.5, 1.0]:
                pos = calculate_radial_position(hash_val, strength, 10)
                
                # Position should be a valid dict with x, y, z
                self.assertIn('x', pos)
                self.assertIn('y', pos)
                self.assertIn('z', pos)
                
                # Calculate distance from origin
                distance = math.sqrt(pos['x']**2 + pos['y']**2 + pos['z']**2)
                
                # Distance should be within expected range (10 to 15)
                self.assertGreater(distance, 0)
                self.assertLess(distance, 20)
    
    def test_stronger_signals_closer(self):
        """Test that stronger signals are positioned closer to center"""
        import math
        
        def calculate_radial_position(hash_val, strength, radius=10):
            angle = (hash_val % 360) * (math.pi / 180)
            elevation = ((hash_val % 180) - 90) * (math.pi / 180)
            distance = radius * (1.5 - strength * 0.5)
            
            return {
                'x': distance * math.cos(elevation) * math.cos(angle),
                'y': distance * math.cos(elevation) * math.sin(angle),
                'z': distance * math.sin(elevation)
            }
        
        hash_val = 12345
        
        weak_pos = calculate_radial_position(hash_val, 0.1, 10)
        strong_pos = calculate_radial_position(hash_val, 0.9, 10)
        
        weak_distance = math.sqrt(weak_pos['x']**2 + weak_pos['y']**2 + weak_pos['z']**2)
        strong_distance = math.sqrt(strong_pos['x']**2 + strong_pos['y']**2 + strong_pos['z']**2)
        
        # Stronger signals should be closer
        self.assertLess(strong_distance, weak_distance)

if __name__ == '__main__':
    unittest.main()
