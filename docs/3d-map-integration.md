# 3D Network Map Integration

## Overview

The 3D Network Map visualizes discovered networks and devices in an interactive Three.js-powered 3D environment.

## Architecture

```
API Backend (Flask)
    ↓
Network Normalizer (src/lib/networkNormalizer.js)
    ↓
3D Scene Builder (Three.js)
    ↓
Interactive Visualization
```

## Data Flow

### 1. Data Acquisition

**Initial Load:**
- Frontend fetches `/api/networks` and `/api/devices`
- Data is normalized using `networkNormalizer.js`
- Nodes are created in 3D scene

**Real-time Updates:**
- WebSocket connection to `ws://127.0.0.1:5000/socket.io/`
- Subscribe to `network_update` events
- Updates are applied incrementally with animations

### 2. Data Normalization

The `networkNormalizer.js` module canonicalizes backend payloads:

```javascript
import { normalizeNetwork } from '../src/lib/networkNormalizer.js';

const rawNetwork = {
  id: 'wifi_1',
  ssid: 'HomeNetwork',
  bssid: '00:1A:2B:3C:4D:5E',
  signal_dbm: -45,
  security: 'WPA2',
  // ... other fields
};

const normalized = normalizeNetwork(rawNetwork);
// normalized.strength = 0.85 (calculated from signal_dbm)
// normalized.hash = 12345 (for deterministic positioning)
```

**Normalized Fields:**

- `strength` (0.0-1.0): Calculated from `signal_dbm` or `rssi`
- `hash`: Deterministic hash for positioning
- All required fields with fallback defaults

### 3. Spatial Positioning

**GPS-based Positioning:**

If GPS coordinates are available:

```javascript
const position = calculateGPSPosition(gps, origin);
// Returns {x, y, z} in 3D space
```

**Radial Positioning (fallback):**

For networks without GPS:

```javascript
const position = calculateRadialPosition(hash, strength, radius);
// Deterministic position based on hash
// Distance from center based on signal strength
```

### 4. Visual Encoding

**Size:**
- Node size = `0.3 + strength * 0.7`
- Stronger signals = larger nodes

**Color:**
- Security-based color mapping:
  - Open: Red (#ff0000)
  - WEP: Orange (#ff6600)
  - WPA: Yellow-orange (#ffaa00)
  - WPA2: Green (#00ff41)
  - WPA3: Cyan (#00ddff)
  - Unknown: Purple (#c000ff)

**Glow/Pulse:**
- Emissive intensity = `0.3 + strength * 0.3`
- Pulse animation based on signal activity

### 5. Interactive Behaviors

**Hover:**
- Tooltip displays full metadata
- Node highlights with increased emissive intensity

**Click:**
- Opens persistent side panel
- Displays detailed information
- Provides actions: Copy MAC/IP, Lookup Vendor, Export JSON

**Double-click:**
- Focuses camera on node with smooth easing animation

**Filters:**
- Security type dropdown
- Signal strength slider
- Vendor filter
- Search box (SSID, MAC, IP)

**Keyboard Shortcuts:**
- `F`: Focus on selected node
- `L`: Toggle labels
- `H`: Toggle HUD
- `ESC`: Close side panel

### 6. Performance Optimization

**GPU Instancing:**

When node count > 200:

```javascript
if (networkNodes.size > 200 && !instancingEnabled) {
  enableInstancing();
}
```

Instanced geometry reduces draw calls significantly.

**Level of Detail (LOD):**

- Far nodes: Simple geometry (8 segments)
- Near nodes: Detailed geometry (16 segments)

**Object Pooling:**

Reuse geometry and materials to reduce memory allocation.

## Component Details

### Network Node

```javascript
{
  geometry: THREE.SphereGeometry,
  material: THREE.MeshPhongMaterial,
  userData: {
    id, ssid, mac, ip, vendor,
    signal_dbm, rssi, channel, frequency,
    security, gps, device_count, last_seen,
    strength, hash, originalColor
  }
}
```

### Animation System

**Entry Animation:**

```javascript
animateNodeEntry(mesh) {
  // Scale from 0.01 to 1.0 with ease-out-cubic
}
```

**Exit Animation:**

```javascript
animateNodeExit(mesh, callback) {
  // Scale to 0 and fade opacity with ease-in-cubic
}
```

**Update Animation:**

```javascript
animateNodeUpdate(mesh, network) {
  // Pulse effect using sine wave
}
```

### WebSocket Event Handling

```javascript
socket.on('network_update', (update) => {
  const { type, data } = update;
  const normalized = normalizeNetwork(data);
  
  switch(type) {
    case 'add':
      addOrUpdateNetwork(normalized);
      break;
    case 'update':
      addOrUpdateNetwork(normalized);
      break;
    case 'remove':
      removeNetwork(normalized.id);
      break;
  }
});
```

## API Contract

### Backend → Frontend

**GET /api/networks:**

```json
{
  "status": "success",
  "networks": [...],
  "total": 10,
  "timestamp": "2025-10-14T12:00:00Z"
}
```

**WebSocket network_update:**

```json
{
  "type": "add|update|remove",
  "data": {
    "id": "wifi_1",
    "ssid": "HomeNetwork",
    ...
  },
  "timestamp": "2025-10-14T12:00:00Z"
}
```

## Debugging

Access debug interface in browser console:

```javascript
window.__mapDebug()
// Returns:
// {
//   sceneNodeCount: 10,
//   isOnline: true,
//   selectedNode: 'wifi_1'
// }
```

## Error Handling

**Offline Mode:**

- Status indicator shows red "OFFLINE"
- Exponential backoff for reconnection attempts
- Cached data remains visible

**Empty State:**

- Displays message: "NO NETWORKS DETECTED"
- HUD remains visible
- Scene is interactive

**API Failures:**

- Graceful fallback to cached data
- Error logged to console
- User notification via status indicator

## Security Considerations

1. **Local Only**: All connections to `127.0.0.1`
2. **No External Calls**: No third-party runtime services
3. **CORS**: Restricted to localhost origins
4. **Input Sanitization**: All user inputs sanitized
5. **Vendor Lookup**: Opens external link (no internal API call)

## Testing

**Unit Tests:**

```bash
npm run test:unit
```

**Smoke Test:**

```bash
npm run smoke:test
```

Verifies:
- API endpoint availability
- Map loads successfully
- Scene has nodes
- UI elements present
- Node interaction works
- No console errors

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires WebGL support.

## Performance Benchmarks

- **< 50 nodes**: 60 FPS
- **50-200 nodes**: 45-60 FPS
- **200-500 nodes**: 30-45 FPS (with instancing)
- **> 500 nodes**: 20-30 FPS (with instancing + LOD)

## Future Enhancements

- [ ] VR/AR support
- [ ] Network topology visualization
- [ ] Traffic flow animations
- [ ] Heat mapping
- [ ] Time-series replay
- [ ] Export to GLTF/OBJ formats
