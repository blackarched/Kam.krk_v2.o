# Device API Documentation

## Overview

The Device API provides endpoints for discovering and managing network devices in CYBER-MATRIX.

## Base URL

```
http://127.0.0.1:5000/api
```

## Authentication

All endpoints require an API key passed in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

## Endpoints

### GET /api/devices

List all discovered devices.

**Response:**

```json
{
  "status": "success",
  "devices": [
    {
      "id": "11:22:33:44:55:66",
      "mac": "11:22:33:44:55:66",
      "ip": "192.168.1.100",
      "hostname": "laptop-john",
      "vendor": "Apple",
      "device_type": "End Device",
      "status": "active",
      "vulnerability_score": 0,
      "last_seen": "2025-10-14T12:00:00Z",
      "signal_dbm": -50,
      "rssi": 75
    }
  ],
  "total": 1,
  "timestamp": "2025-10-14T12:05:00Z"
}
```

**Fields:**

- `id` (string): Unique identifier (MAC or IP)
- `mac` (string): MAC address
- `ip` (string|null): IP address
- `hostname` (string): Device hostname
- `vendor` (string): Device vendor/manufacturer
- `device_type` (string): Type of device
- `status` (string): Device status (active, inactive)
- `vulnerability_score` (number): Vulnerability score (0-100)
- `last_seen` (string): ISO8601 timestamp of last activity
- `signal_dbm` (number): Signal strength in dBm
- `rssi` (number): Signal strength percentage (0-100)

### GET /api/devices/:mac

Get details of a specific device by MAC address.

**Parameters:**

- `mac` (path): Device MAC address (format: XX:XX:XX:XX:XX:XX)

**Response:**

```json
{
  "status": "success",
  "device": {
    "id": "11:22:33:44:55:66",
    "mac": "11:22:33:44:55:66",
    "ip": "192.168.1.100",
    "hostname": "laptop-john",
    "vendor": "Apple",
    "device_type": "End Device",
    "status": "active",
    "vulnerability_score": 0,
    "last_seen": "2025-10-14T12:00:00Z"
  }
}
```

**Error Response (404):**

```json
{
  "error": "Device not found"
}
```

## Device Discovery

Devices are discovered through multiple methods:

1. **ARP Table Scanning**: Reads system ARP cache
2. **Ping Sweep**: Active ICMP ping to detect hosts
3. **Port Scanning**: Identifies open ports and services
4. **DNS Resolution**: Resolves hostnames when possible

## Device Types

- `Unknown`: Type not identified
- `End Device`: End-user devices (laptops, phones, tablets)
- `Server/Network Device`: Servers, routers, switches
- `IoT Device`: Internet of Things devices
- `Printer`: Network printers
- `Access Point`: WiFi access points

## Vulnerability Scoring

Vulnerability scores are calculated based on:

- Open ports and exposed services
- Operating system detection
- Known CVEs and exploits
- Security posture

Score ranges:

- `0-30`: Low risk
- `31-60`: Medium risk
- `61-80`: High risk
- `81-100`: Critical risk

## Security

- All endpoints bind to `127.0.0.1` only
- CORS restricted to localhost
- Input validation and sanitization
- No shell command injection vulnerabilities
- Rate limited to prevent abuse

## Error Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid/missing API key)
- `404` - Device not found
- `429` - Rate limit exceeded
- `500` - Internal server error

## Example Usage

### Python

```python
import requests

API_KEY = 'your-api-key'
BASE_URL = 'http://127.0.0.1:5000/api'

def get_devices():
    headers = {'X-API-Key': API_KEY}
    response = requests.get(f'{BASE_URL}/devices', headers=headers)
    data = response.json()
    return data['devices']

devices = get_devices()
for device in devices:
    print(f"{device['hostname']} ({device['ip']}) - {device['vendor']}")
```

### JavaScript

```javascript
const API_KEY = 'your-api-key';

async function getDevice(mac) {
  const response = await fetch(`http://127.0.0.1:5000/api/devices/${mac}`, {
    headers: {
      'X-API-Key': API_KEY
    }
  });
  const data = await response.json();
  return data.device;
}

getDevice('11:22:33:44:55:66').then(device => {
  console.log(device);
});
```

## Database

Device data is stored in SQLite database `cyber_matrix.db`:

**Table: network_devices**

```sql
CREATE TABLE network_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    mac_address TEXT,
    hostname TEXT,
    device_type TEXT DEFAULT 'Unknown',
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    vulnerability_score INTEGER DEFAULT 0
);
```

## Notes

- Device discovery runs asynchronously
- Devices are marked inactive after 1 hour of inactivity
- MAC vendor lookup uses IEEE OUI database
- Hostname resolution may fail for devices with strict firewall rules
