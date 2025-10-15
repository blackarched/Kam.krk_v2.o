# CYBER-MATRIX 3D Network Map - Installation & Testing Guide

## Quick Start

Follow these commands exactly to run the complete 3D network map with all features:

### 1. Install Dependencies

```bash
npm ci
pip3 install -r requirements.txt
```

### 2. Run Development Server

```bash
npm run dev
```

The server will start at `http://127.0.0.1:5000`

- Main dashboard: `http://127.0.0.1:5000/`
- 3D Map: `http://127.0.0.1:5000/static/3d-map.html`
- API endpoint: `http://127.0.0.1:5000/api/networks`
- WebSocket: `ws://127.0.0.1:5000/socket.io/`

### 3. Run Smoke Test

```bash
npm run smoke:test
```

This will:
1. Start the dev server automatically
2. Wait for the server to be ready
3. Run all smoke tests
4. Generate output files
5. Stop the server

### Test Output Files

After running `npm run smoke:test`, check these files:

- **Screenshot**: `test/output/after_vivid.png`
- **Logs**: `test/output/smoke-log.txt`

### 4. View the 3D Map

Open `http://127.0.0.1:5000/static/3d-map.html` in your browser.

The map will:
- Display all discovered networks in 3D space
- Show real-time updates via WebSocket
- Provide interactive hover tooltips
- Allow clicking nodes for detailed info
- Support filtering and search
- Respond to keyboard shortcuts (F, L, H, ESC)

## API Endpoints

### GET /api/networks

Returns all discovered networks with canonical fields:

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
      "security": "WPA2",
      "gps": null,
      "device_count": 5,
      "last_seen": "2025-10-14T12:00:00Z"
    }
  ],
  "total": 1,
  "timestamp": "2025-10-14T12:05:00Z"
}
```

### GET /api/devices

Returns all discovered devices:

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

### WebSocket /ws/networks

Connect to `ws://127.0.0.1:5000/socket.io/` for real-time updates:

```javascript
const socket = io('http://127.0.0.1:5000');

socket.on('connect', () => {
  socket.emit('subscribe_networks');
});

socket.on('network_update', (update) => {
  console.log(update.type); // 'add', 'update', or 'remove'
  console.log(update.data); // Network data
});
```

## Running Tests

### Unit Tests

```bash
npm run test:unit
```

Tests API endpoints and data normalization.

### Smoke Tests

```bash
npm run smoke:test
```

End-to-end test that verifies:
- API endpoint availability (GET /api/networks returns 200)
- 3D map loads successfully
- Scene has >= 1 nodes (or shows empty state)
- Node interaction works (click opens side panel)
- No console errors
- Screenshot is captured

### All Tests

```bash
npm run test:all
```

Runs both unit and smoke tests.

## Features Implemented

### Backend
✅ GET /api/networks - List all networks  
✅ GET /api/networks/:id - Get network details  
✅ GET /api/devices - List all devices  
✅ GET /api/devices/:mac - Get device details  
✅ WebSocket /ws/networks - Real-time updates  
✅ Network discovery from WiFi and ARP scans  
✅ Secure tools with input validation  
✅ Database persistence (SQLite)  

### Frontend
✅ 3D visualization with Three.js  
✅ Network normalizer module (src/lib/networkNormalizer.js)  
✅ Real-time WebSocket updates  
✅ Interactive hover tooltips  
✅ Click for detailed side panel  
✅ Double-click to focus/zoom  
✅ Filters: security, strength, vendor, search  
✅ Keyboard shortcuts (F, L, H, ESC)  
✅ GPS-based or radial positioning  
✅ Visual encoding (size, color, glow by signal/security)  
✅ Empty state display  
✅ Offline indicator  
✅ GPU instancing support (for >200 nodes)  
✅ LOD and object pooling  

### Tests
✅ Unit tests for API endpoints  
✅ Unit tests for normalizer logic  
✅ Smoke test with Puppeteer  
✅ Test fixtures (sampleNetworks.json)  
✅ Screenshot capture  
✅ Log output  

### Documentation
✅ docs/network-api.md  
✅ docs/device-api.md  
✅ docs/3d-map-integration.md  
✅ README-FIX.md (this file)  

## Architecture

```
Backend (Flask + SocketIO)
    ↓ REST API
Normalizer (src/lib/networkNormalizer.js)
    ↓ Canonical data
3D Scene (Three.js)
    ↓ WebSocket updates
Interactive Visualization
```

## Security

- Server binds to `127.0.0.1` only
- CORS restricted to localhost
- No external runtime calls
- Input validation and sanitization
- SQL injection protection
- Rate limiting on API endpoints

## Troubleshooting

### Server won't start

```bash
# Check if port 5000 is in use
lsof -ti:5000 | xargs kill -9

# Restart
npm run dev
```

### No networks detected

1. Ensure you have wireless interface available
2. Run a network scan manually:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/network/scan \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-key" \
     -d '{"ip_range": "192.168.1.0/24"}'
   ```

### Smoke test fails

1. Ensure server is not already running
2. Check test output logs: `test/output/smoke-log.txt`
3. View screenshot: `test/output/after_vivid.png`
4. Run manually:
   ```bash
   npm run dev &
   sleep 5
   node test/smoke/map-smoke.js
   ```

### 3D map is blank

1. Check browser console for errors
2. Verify API returns data: `curl http://127.0.0.1:5000/api/networks`
3. Check WebSocket connection in browser dev tools
4. Try running `window.__mapDebug()` in console

## File Structure

```
/workspace
├── app.py                          # Main Flask backend
├── src/
│   └── lib/
│       └── networkNormalizer.js    # Data normalizer module
├── static/
│   └── 3d-map.html                 # 3D visualization page
├── test/
│   ├── fixtures/
│   │   └── sampleNetworks.json     # Test data
│   ├── unit/
│   │   ├── test_network_api.py     # API unit tests
│   │   └── test_normalizer.py      # Normalizer unit tests
│   ├── smoke/
│   │   └── map-smoke.js            # Smoke test
│   ├── output/                     # Test output
│   │   ├── after_vivid.png         # Screenshot
│   │   └── smoke-log.txt           # Log output
│   └── run_smoke.js                # Test runner
├── docs/
│   ├── network-api.md              # Network API docs
│   ├── device-api.md               # Device API docs
│   └── 3d-map-integration.md       # Integration guide
├── package.json                    # NPM scripts
├── requirements.txt                # Python dependencies
└── README-FIX.md                   # This file
```

## Commands Summary

| Command | Description |
|---------|-------------|
| `npm ci` | Install dependencies |
| `npm run dev` | Start dev server |
| `npm run smoke:test` | Run smoke tests |
| `npm run test:unit` | Run unit tests |
| `npm run test:all` | Run all tests |

## Success Criteria

After running the commands above:

✅ `npm run dev` starts successfully (no extra steps)  
✅ GET `http://127.0.0.1:5000/api/networks` returns 200 with canonical fields  
✅ 3D map at `/static/3d-map.html` shows non-blank scene within 5s  
✅ `window.__mapDebug().sceneNodeCount >= 1` or empty state displayed  
✅ `npm run smoke:test` exits 0  
✅ `test/output/after_vivid.png` and `test/output/smoke-log.txt` created  
✅ No console uncaught exceptions  
✅ Network/device info displayed directly in 3D map  
✅ Interactive behaviors work (hover, click, focus, filters)  

## Next Steps

1. Run `npm ci` to install dependencies
2. Run `pip3 install -r requirements.txt` to install Python packages
3. Run `npm run dev` to start the server
4. Open `http://127.0.0.1:5000/static/3d-map.html` in your browser
5. Run `npm run smoke:test` to verify everything works
6. Check `test/output/` for test results

Enjoy the CYBER-MATRIX 3D Network Map! 🚀
