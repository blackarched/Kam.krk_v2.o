/**
 * Network Data Normalizer
 * Canonicalizes backend payloads into standardized format for 3D visualization
 */

/**
 * Calculate signal strength from dBm
 * @param {number} dbm - Signal strength in dBm (-100 to 0)
 * @returns {number} Normalized strength (0.0 to 1.0)
 */
function calculateStrength(dbm) {
    if (dbm === null || dbm === undefined) return 0.5;
    // -100 dBm is very weak, -30 dBm is excellent
    const min = -100;
    const max = -30;
    const clamped = Math.max(min, Math.min(max, dbm));
    return (clamped - min) / (max - min);
}

/**
 * Calculate signal strength from RSSI percentage
 * @param {number} rssi - Signal strength percentage (0-100)
 * @returns {number} Normalized strength (0.0 to 1.0)
 */
function calculateStrengthFromRSSI(rssi) {
    if (rssi === null || rssi === undefined) return 0.5;
    return Math.max(0, Math.min(1, rssi / 100));
}

/**
 * Generate deterministic hash from string
 * @param {string} str - Input string
 * @returns {number} Hash value (0 to 2^32)
 */
function hashString(str) {
    let hash = 0;
    if (!str || str.length === 0) return hash;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
}

/**
 * Normalize network data from backend API
 * @param {Object} rawNetwork - Raw network data from backend
 * @returns {Object} Normalized network data
 */
export function normalizeNetwork(rawNetwork) {
    const {
        id,
        ssid,
        bssid,
        mac,
        ip,
        vendor,
        signal_dbm,
        rssi,
        channel,
        frequency,
        security,
        gps,
        device_count,
        last_seen
    } = rawNetwork;

    // Calculate strength from available signals
    let strength;
    if (signal_dbm !== null && signal_dbm !== undefined) {
        strength = calculateStrength(signal_dbm);
    } else if (rssi !== null && rssi !== undefined) {
        strength = calculateStrengthFromRSSI(rssi);
    } else {
        strength = 0.5;
    }

    return {
        id: id || mac || bssid || `network_${Math.random()}`,
        ssid: ssid || 'Unknown Network',
        bssid: bssid || mac || '00:00:00:00:00:00',
        mac: mac || bssid || '00:00:00:00:00:00',
        ip: ip || null,
        vendor: vendor || 'Unknown',
        signal_dbm: signal_dbm ?? -70,
        rssi: rssi ?? 50,
        channel: channel ?? 1,
        frequency: frequency ?? 2412,
        security: security || 'Unknown',
        gps: gps || null,
        device_count: device_count ?? 0,
        last_seen: last_seen || new Date().toISOString(),
        strength: strength,
        // Add hash for deterministic positioning
        hash: hashString(bssid || mac || id || ssid)
    };
}

/**
 * Normalize device data from backend API
 * @param {Object} rawDevice - Raw device data from backend
 * @returns {Object} Normalized device data
 */
export function normalizeDevice(rawDevice) {
    const {
        id,
        mac,
        ip,
        hostname,
        vendor,
        device_type,
        status,
        vulnerability_score,
        last_seen,
        signal_dbm,
        rssi
    } = rawDevice;

    // Calculate strength
    let strength;
    if (signal_dbm !== null && signal_dbm !== undefined) {
        strength = calculateStrength(signal_dbm);
    } else if (rssi !== null && rssi !== undefined) {
        strength = calculateStrengthFromRSSI(rssi);
    } else {
        strength = 0.6; // Default for devices
    }

    return {
        id: id || mac || ip || `device_${Math.random()}`,
        mac: mac || '00:00:00:00:00:00',
        ip: ip || null,
        hostname: hostname || ip || 'Unknown Device',
        vendor: vendor || device_type || 'Unknown',
        device_type: device_type || 'Unknown',
        status: status || 'active',
        vulnerability_score: vulnerability_score ?? 0,
        last_seen: last_seen || new Date().toISOString(),
        signal_dbm: signal_dbm ?? -50,
        rssi: rssi ?? 70,
        strength: strength,
        // Add hash for deterministic positioning
        hash: hashString(mac || ip || id)
    };
}

/**
 * Normalize array of networks
 * @param {Array} networks - Array of raw network data
 * @returns {Array} Array of normalized networks
 */
export function normalizeNetworks(networks) {
    if (!Array.isArray(networks)) return [];
    return networks.map(normalizeNetwork);
}

/**
 * Normalize array of devices
 * @param {Array} devices - Array of raw device data
 * @returns {Array} Array of normalized devices
 */
export function normalizeDevices(devices) {
    if (!Array.isArray(devices)) return [];
    return devices.map(normalizeDevice);
}

/**
 * Get security color based on security type
 * @param {string} security - Security type
 * @returns {string} Hex color code
 */
export function getSecurityColor(security) {
    const securityColors = {
        'Open': '#ff0000',        // Red - dangerous
        'WEP': '#ff6600',          // Orange - weak
        'WPA': '#ffaa00',          // Yellow-orange - moderate
        'WPA2': '#00ff41',         // Green - good
        'WPA3': '#00ddff',         // Cyan - excellent
        'Unknown': '#c000ff'       // Purple - unknown
    };
    
    return securityColors[security] || securityColors['Unknown'];
}

/**
 * Get vendor color (deterministic based on vendor name)
 * @param {string} vendor - Vendor name
 * @returns {string} Hex color code
 */
export function getVendorColor(vendor) {
    if (!vendor || vendor === 'Unknown') return '#999999';
    
    const hash = hashString(vendor);
    const hue = hash % 360;
    const saturation = 70 + (hash % 30);
    const lightness = 50 + (hash % 20);
    
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

/**
 * Calculate radial position for 3D space (deterministic)
 * @param {number} hash - Hash value for deterministic positioning
 * @param {number} strength - Signal strength (0-1)
 * @param {number} radius - Base radius
 * @returns {Object} Position {x, y, z}
 */
export function calculateRadialPosition(hash, strength, radius = 10) {
    // Use hash for deterministic angle
    const angle = (hash % 360) * (Math.PI / 180);
    const elevation = ((hash % 180) - 90) * (Math.PI / 180);
    
    // Stronger signals closer to center
    const distance = radius * (1.5 - strength * 0.5);
    
    return {
        x: distance * Math.cos(elevation) * Math.cos(angle),
        y: distance * Math.cos(elevation) * Math.sin(angle),
        z: distance * Math.sin(elevation)
    };
}

/**
 * Calculate GPS-based position for 3D space
 * @param {Object} gps - GPS coordinates {lat, lon, alt}
 * @param {Object} origin - Origin GPS coordinates
 * @returns {Object} Position {x, y, z}
 */
export function calculateGPSPosition(gps, origin) {
    if (!gps || !gps.lat || !gps.lon) return null;
    
    const R = 6371000; // Earth radius in meters
    const lat1 = origin.lat * Math.PI / 180;
    const lat2 = gps.lat * Math.PI / 180;
    const dLat = lat2 - lat1;
    const dLon = (gps.lon - origin.lon) * Math.PI / 180;
    
    const x = R * dLon * Math.cos((lat1 + lat2) / 2);
    const y = gps.alt || 0;
    const z = R * dLat;
    
    // Scale to reasonable 3D space (1 unit = 10 meters)
    return {
        x: x / 10,
        y: y / 10,
        z: z / 10
    };
}

// Export all functions as named exports and default export
export default {
    normalizeNetwork,
    normalizeDevice,
    normalizeNetworks,
    normalizeDevices,
    calculateStrength,
    calculateStrengthFromRSSI,
    getSecurityColor,
    getVendorColor,
    calculateRadialPosition,
    calculateGPSPosition,
    hashString
};
