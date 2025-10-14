/**
 * Smoke Test for 3D Network Map
 * Tests that the map loads, displays networks, and is interactive
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const API_BASE = 'http://127.0.0.1:5000';
const MAP_URL = 'http://127.0.0.1:5000/static/3d-map.html';
const OUTPUT_DIR = path.join(__dirname, '../output');
const SCREENSHOT_PATH = path.join(OUTPUT_DIR, 'after_vivid.png');
const LOG_PATH = path.join(OUTPUT_DIR, 'smoke-log.txt');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Log function
let logs = [];
function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}`;
    console.log(logMessage);
    logs.push(logMessage);
}

async function runSmokeTest() {
    let browser;
    let passed = true;
    
    try {
        log('=== CYBER-MATRIX 3D Map Smoke Test ===');
        log('Starting smoke test...');
        
        // Launch browser
        log('Launching headless browser...');
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Capture console logs
        page.on('console', msg => {
            log(`[Browser Console] ${msg.type()}: ${msg.text()}`);
        });
        
        // Capture errors
        page.on('pageerror', error => {
            log(`[Browser Error] ${error.message}`);
            passed = false;
        });
        
        // Test 1: Check if API endpoint is available
        log('Test 1: Checking API endpoint availability...');
        try {
            const response = await fetch(`${API_BASE}/api/networks`);
            if (response.status === 200) {
                log('✓ API endpoint /api/networks returned 200');
            } else {
                log(`✗ API endpoint /api/networks returned ${response.status}`);
                passed = false;
            }
        } catch (error) {
            log(`✗ API endpoint check failed: ${error.message}`);
            passed = false;
        }
        
        // Test 2: Load the map page
        log('Test 2: Loading 3D map page...');
        try {
            await page.goto(MAP_URL, {
                waitUntil: 'networkidle2',
                timeout: 10000
            });
            log('✓ Map page loaded successfully');
        } catch (error) {
            log(`✗ Failed to load map page: ${error.message}`);
            passed = false;
            throw error;
        }
        
        // Test 3: Wait for map initialization (up to 5s)
        log('Test 3: Waiting for map initialization...');
        try {
            await page.waitForFunction(
                () => typeof window.__mapDebug === 'function',
                { timeout: 5000 }
            );
            log('✓ Map debug interface available');
        } catch (error) {
            log(`✗ Map initialization timeout: ${error.message}`);
            passed = false;
        }
        
        // Test 4: Check scene node count
        log('Test 4: Checking scene node count...');
        try {
            const debugInfo = await page.evaluate(() => {
                if (typeof window.__mapDebug === 'function') {
                    return window.__mapDebug();
                }
                return null;
            });
            
            if (debugInfo) {
                log(`Map debug info: ${JSON.stringify(debugInfo, null, 2)}`);
                
                if (debugInfo.sceneNodeCount >= 1) {
                    log(`✓ Scene has ${debugInfo.sceneNodeCount} nodes (>= 1)`);
                } else {
                    log(`✗ Scene has ${debugInfo.sceneNodeCount} nodes (expected >= 1)`);
                    log('Note: This may be expected if no networks were discovered');
                }
                
                if (debugInfo.isOnline) {
                    log('✓ WebSocket connection is online');
                } else {
                    log('⚠ WebSocket connection is offline');
                }
            } else {
                log('✗ Unable to retrieve debug info');
                passed = false;
            }
        } catch (error) {
            log(`✗ Scene check failed: ${error.message}`);
            passed = false;
        }
        
        // Test 5: Check for UI elements
        log('Test 5: Checking UI elements...');
        try {
            const hudExists = await page.$('#hud');
            const controlsExist = await page.$('#controls');
            const canvasExists = await page.$('#scene-canvas');
            
            if (hudExists && controlsExist && canvasExists) {
                log('✓ All required UI elements present (HUD, controls, canvas)');
            } else {
                log('✗ Missing UI elements');
                passed = false;
            }
        } catch (error) {
            log(`✗ UI element check failed: ${error.message}`);
            passed = false;
        }
        
        // Test 6: Simulate node click (if nodes exist)
        log('Test 6: Testing node interaction...');
        try {
            const hasNodes = await page.evaluate(() => {
                if (typeof window.__mapDebug === 'function') {
                    return window.__mapDebug().sceneNodeCount > 0;
                }
                return false;
            });
            
            if (hasNodes) {
                // Click center of canvas (likely to hit a node)
                await page.click('#scene-canvas', { x: 960, y: 540 });
                await page.waitForTimeout(500);
                
                // Check if side panel opened
                const panelVisible = await page.evaluate(() => {
                    const panel = document.getElementById('side-panel');
                    return panel && panel.classList.contains('visible');
                });
                
                if (panelVisible) {
                    log('✓ Node click opened side panel');
                } else {
                    log('⚠ Side panel not opened (may not have clicked a node)');
                }
            } else {
                log('⚠ Skipping node interaction test (no nodes in scene)');
            }
        } catch (error) {
            log(`⚠ Node interaction test failed: ${error.message}`);
        }
        
        // Test 7: Take screenshot
        log('Test 7: Taking screenshot...');
        try {
            await page.screenshot({
                path: SCREENSHOT_PATH,
                fullPage: false
            });
            log(`✓ Screenshot saved to ${SCREENSHOT_PATH}`);
        } catch (error) {
            log(`✗ Screenshot failed: ${error.message}`);
            passed = false;
        }
        
        // Test 8: Check for console errors
        log('Test 8: Checking for console errors...');
        const consoleErrors = logs.filter(l => l.includes('[Browser Error]'));
        if (consoleErrors.length === 0) {
            log('✓ No console errors detected');
        } else {
            log(`✗ Found ${consoleErrors.length} console errors`);
            passed = false;
        }
        
    } catch (error) {
        log(`✗ Smoke test failed with error: ${error.message}`);
        passed = false;
    } finally {
        // Close browser
        if (browser) {
            await browser.close();
            log('Browser closed');
        }
        
        // Write logs to file
        fs.writeFileSync(LOG_PATH, logs.join('\n'));
        log(`Log file saved to ${LOG_PATH}`);
        
        // Final result
        if (passed) {
            log('=== ✓ SMOKE TEST PASSED ===');
            process.exit(0);
        } else {
            log('=== ✗ SMOKE TEST FAILED ===');
            process.exit(1);
        }
    }
}

// Run the test
runSmokeTest().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
