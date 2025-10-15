#!/usr/bin/env python3
"""
Unit tests for Network API endpoints
"""

import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import app, init_database

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_database()
        yield client

def test_networks_endpoint_exists(client):
    """Test that /api/networks endpoint exists"""
    response = client.get('/api/networks')
    assert response.status_code in [200, 401]  # 401 if API key required

def test_networks_endpoint_returns_json(client):
    """Test that /api/networks returns JSON"""
    response = client.get('/api/networks')
    assert response.content_type == 'application/json'

def test_networks_response_structure(client):
    """Test that /api/networks response has correct structure"""
    response = client.get('/api/networks')
    data = json.loads(response.data)
    
    # Should have status, networks, and total fields
    assert 'status' in data or 'error' in data
    if 'status' in data:
        assert 'networks' in data
        assert 'total' in data
        assert isinstance(data['networks'], list)

def test_network_detail_endpoint(client):
    """Test that /api/networks/:id endpoint works"""
    response = client.get('/api/networks/wifi_1')
    assert response.status_code in [200, 404, 401]
    assert response.content_type == 'application/json'

def test_network_canonicalization(client):
    """Test that network data has canonical fields"""
    response = client.get('/api/networks')
    data = json.loads(response.data)
    
    if 'networks' in data and len(data['networks']) > 0:
        network = data['networks'][0]
        
        # Required canonical fields
        required_fields = ['id', 'ssid', 'bssid', 'mac', 'last_seen']
        for field in required_fields:
            assert field in network, f"Missing required field: {field}"
        
        # Optional but expected fields
        expected_fields = ['ip', 'vendor', 'signal_dbm', 'rssi', 'channel', 
                          'frequency', 'security', 'gps', 'device_count']
        for field in expected_fields:
            assert field in network, f"Missing expected field: {field}"

def test_network_data_types(client):
    """Test that network data types are correct"""
    response = client.get('/api/networks')
    data = json.loads(response.data)
    
    if 'networks' in data and len(data['networks']) > 0:
        network = data['networks'][0]
        
        # Type checks
        assert isinstance(network['id'], str)
        assert isinstance(network['ssid'], str)
        assert isinstance(network['bssid'], str)
        assert isinstance(network['mac'], str)
        assert network['ip'] is None or isinstance(network['ip'], str)
        assert isinstance(network['vendor'], str)
        assert isinstance(network['signal_dbm'], (int, float))
        assert isinstance(network['rssi'], (int, float))
        assert isinstance(network['channel'], int)
        assert isinstance(network['frequency'], int)
        assert isinstance(network['security'], str)
        assert isinstance(network['device_count'], int)
        assert isinstance(network['last_seen'], str)

def test_network_timestamp_format(client):
    """Test that timestamps are in ISO8601 format"""
    response = client.get('/api/networks')
    data = json.loads(response.data)
    
    if 'networks' in data and len(data['networks']) > 0:
        network = data['networks'][0]
        
        # Should be able to parse as ISO8601
        from datetime import datetime
        try:
            datetime.fromisoformat(network['last_seen'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid ISO8601 timestamp: {network['last_seen']}")

def test_devices_endpoint_exists(client):
    """Test that /api/devices endpoint exists"""
    response = client.get('/api/devices')
    assert response.status_code in [200, 401]
    assert response.content_type == 'application/json'

def test_devices_response_structure(client):
    """Test that /api/devices response has correct structure"""
    response = client.get('/api/devices')
    data = json.loads(response.data)
    
    assert 'status' in data or 'error' in data
    if 'status' in data:
        assert 'devices' in data
        assert 'total' in data
        assert isinstance(data['devices'], list)

def test_device_detail_endpoint(client):
    """Test that /api/devices/:mac endpoint works"""
    response = client.get('/api/devices/00:11:22:33:44:55')
    assert response.status_code in [200, 404, 401]
    assert response.content_type == 'application/json'

def test_device_canonicalization(client):
    """Test that device data has canonical fields"""
    response = client.get('/api/devices')
    data = json.loads(response.data)
    
    if 'devices' in data and len(data['devices']) > 0:
        device = data['devices'][0]
        
        # Required canonical fields
        required_fields = ['id', 'mac', 'ip', 'hostname', 'vendor', 
                          'device_type', 'status', 'last_seen']
        for field in required_fields:
            assert field in device, f"Missing required field: {field}"

def test_malformed_network_id(client):
    """Test that malformed network ID is handled"""
    response = client.get('/api/networks/invalid<>id')
    assert response.status_code in [404, 400, 500]

def test_malformed_device_mac(client):
    """Test that malformed device MAC is handled"""
    response = client.get('/api/devices/invalid;mac')
    assert response.status_code in [404, 400, 500]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
