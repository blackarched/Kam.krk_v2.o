# Network API Documentation

## Overview

The Network API provides endpoints for discovering and managing network resources in CYBER-MATRIX.

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

### GET /api/networks

List all discovered networks.

**Response:**

```json
{
  "status": "success",
  "networks": [
    {
      "id": "wifi_1",
      "ssid": "HomeNetwork-5G",
      "bssid": "00:1A:2B:3C:4D:5E",
      "mac": "00:1A:2B:3C:4D:5E",
      "ip": null,
      "vendor": "Cisco",
      "signal_dbm": -45,
      "rssi": 85,
      "channel": 36,
      "frequency": 5180,
      "security": "WPA3",
      "gps": null,
      "device_count": 5,
      "last_seen": "2025-10-14T12:00:00Z"
    }
  ],
  "total": 1,
  "timestamp": "2025-10-14T12:05:00Z"
}
```

**Fields:**

- `id` (string): Unique identifier
- `ssid` (string): Network name
- `bssid` (string): BSSID (MAC address of access point)
- `mac` (string): MAC address
- `ip` (string|null): IP address if available
- `vendor` (string): Device vendor
- `signal_dbm` (number): Signal strength in dBm (-100 to 0)
- `rssi` (number): Signal strength percentage (0-100)
- `channel` (number): WiFi channel
- `frequency` (number): Frequency in MHz
- `security` (string): Security type (Open, WEP, WPA, WPA2, WPA3)
- `gps` (object|null): GPS coordinates {lat, lon, alt}
- `device_count` (number): Number of devices on network
- `last_seen` (string): ISO8601 timestamp

### GET /api/networks/:id

Get details of a specific network.

**Parameters:**

- `id` (path): Network ID

**Response:**

```json
{
  "status": "success",
  "network": {
    "id": "wifi_1",
    "ssid": "HomeNetwork-5G",
    "bssid": "00:1A:2B:3C:4D:5E",
    "mac": "00:1A:2B:3C:4D:5E",
    "channel": 36,
    "frequency": 5180,
    "security": "WPA3",
    "signal_dbm": -45,
    "last_seen": "2025-10-14T12:00:00Z"
  }
}
```

**Error Response (404):**

```json
{
  "error": "Network not found"
}
```

## WebSocket API

### Connection

Connect to WebSocket at:

```
ws://127.0.0.1:5000/socket.io/
```

### Events

#### Client → Server

**subscribe_networks**

Subscribe to network updates.

```javascript
socket.emit('subscribe_networks');
```

#### Server → Client

**connected**

Emitted when connection is established.

```json
{
  "status": "connected",
  "message": "Connected to CYBER-MATRIX"
}
```

**network_update**

Emitted when a network is added, updated, or removed.

```json
{
  "type": "add|update|remove",
  "data": {
    "id": "wifi_1",
    "ssid": "HomeNetwork-5G",
    ...
  },
  "timestamp": "2025-10-14T12:05:00Z"
}
```

## Error Codes

- `200` - Success
- `401` - Unauthorized (invalid/missing API key)
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Internal server error

## Rate Limiting

- 100 requests per minute per IP address
- WebSocket updates are not rate limited

## Security

- All endpoints bind to `127.0.0.1` only
- CORS restricted to localhost only
- No external third-party calls
- Input validation on all parameters
- SQL injection protection via parameterized queries

## Example Usage

### JavaScript (Fetch)

```javascript
const API_KEY = 'your-api-key';

async function getNetworks() {
  const response = await fetch('http://127.0.0.1:5000/api/networks', {
    headers: {
      'X-API-Key': API_KEY
    }
  });
  const data = await response.json();
  console.log(data.networks);
}
```

### JavaScript (WebSocket)

```javascript
const socket = io('http://127.0.0.1:5000');

socket.on('connect', () => {
  console.log('Connected');
  socket.emit('subscribe_networks');
});

socket.on('network_update', (update) => {
  console.log('Network update:', update.type, update.data);
});
```

## Notes

- Network discovery runs continuously in the background
- Database persists discovered networks
- Inactive networks are marked but not immediately removed
- GPS coordinates are optional and depend on device capabilities
