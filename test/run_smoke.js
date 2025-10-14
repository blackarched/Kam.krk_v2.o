#!/usr/bin/env node
/**
 * Smoke Test Runner
 * Starts the dev server and runs smoke tests
 */

const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

const SERVER_PORT = 5000;
const SERVER_HOST = '127.0.0.1';
const STARTUP_TIMEOUT = 15000; // 15 seconds
const SHUTDOWN_TIMEOUT = 5000; // 5 seconds

let serverProcess = null;

function log(message) {
    console.log(`[Smoke Runner] ${message}`);
}

function checkServerReady() {
    return new Promise((resolve) => {
        const options = {
            hostname: SERVER_HOST,
            port: SERVER_PORT,
            path: '/api/networks',
            method: 'GET',
            timeout: 2000
        };
        
        const req = http.request(options, (res) => {
            resolve(res.statusCode === 200 || res.statusCode === 401);
        });
        
        req.on('error', () => resolve(false));
        req.on('timeout', () => {
            req.destroy();
            resolve(false);
        });
        
        req.end();
    });
}

async function waitForServer(timeout) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
        if (await checkServerReady()) {
            return true;
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    return false;
}

async function startServer() {
    log('Starting dev server...');
    
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    serverProcess = spawn(pythonPath, ['app.py'], {
        cwd: path.join(__dirname, '..'),
        env: { ...process.env, CYBER_MATRIX_HOST: SERVER_HOST, CYBER_MATRIX_PORT: SERVER_PORT.toString() },
        stdio: ['ignore', 'pipe', 'pipe']
    });
    
    serverProcess.stdout.on('data', (data) => {
        log(`[Server] ${data.toString().trim()}`);
    });
    
    serverProcess.stderr.on('data', (data) => {
        log(`[Server Error] ${data.toString().trim()}`);
    });
    
    serverProcess.on('close', (code) => {
        log(`Server process exited with code ${code}`);
    });
    
    log(`Waiting for server to be ready (timeout: ${STARTUP_TIMEOUT}ms)...`);
    const ready = await waitForServer(STARTUP_TIMEOUT);
    
    if (!ready) {
        throw new Error('Server failed to start within timeout');
    }
    
    log('✓ Server is ready');
}

function stopServer() {
    return new Promise((resolve) => {
        if (!serverProcess) {
            resolve();
            return;
        }
        
        log('Stopping server...');
        
        const timeout = setTimeout(() => {
            log('Force killing server...');
            serverProcess.kill('SIGKILL');
            resolve();
        }, SHUTDOWN_TIMEOUT);
        
        serverProcess.on('close', () => {
            clearTimeout(timeout);
            log('Server stopped');
            resolve();
        });
        
        serverProcess.kill('SIGTERM');
    });
}

async function runTests() {
    log('Running smoke tests...');
    
    return new Promise((resolve, reject) => {
        const testProcess = spawn('node', [path.join(__dirname, 'smoke', 'map-smoke.js')], {
            stdio: 'inherit'
        });
        
        testProcess.on('close', (code) => {
            if (code === 0) {
                log('✓ Smoke tests passed');
                resolve();
            } else {
                log(`✗ Smoke tests failed with code ${code}`);
                reject(new Error(`Tests failed with code ${code}`));
            }
        });
        
        testProcess.on('error', (error) => {
            log(`✗ Test execution error: ${error.message}`);
            reject(error);
        });
    });
}

async function main() {
    log('=== CYBER-MATRIX Smoke Test Runner ===');
    
    let exitCode = 0;
    
    try {
        await startServer();
        await runTests();
        log('=== ✓ ALL TESTS PASSED ===');
    } catch (error) {
        log(`=== ✗ TESTS FAILED: ${error.message} ===`);
        exitCode = 1;
    } finally {
        await stopServer();
    }
    
    process.exit(exitCode);
}

// Handle cleanup on exit
process.on('SIGINT', async () => {
    log('Received SIGINT, cleaning up...');
    await stopServer();
    process.exit(1);
});

process.on('SIGTERM', async () => {
    log('Received SIGTERM, cleaning up...');
    await stopServer();
    process.exit(1);
});

// Run
main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
