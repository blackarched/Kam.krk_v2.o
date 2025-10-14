# CYBER-MATRIX v8.0 - Project Knowledge Base for MCP-Enhanced Development

## 🎯 Purpose

This file provides comprehensive project knowledge for AI assistants using MCP servers.
Read this file at the start of any session to understand the project structure, patterns, and critical information.

---

## 📁 Project Architecture

### Core Concept: Dual Implementation Strategy

CYBER-MATRIX v8.0 maintains **TWO parallel implementations** of all network/security functionality:

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURE (Default)                         │
├─────────────────────────────────────────────────────────────┤
│  secure_network_tools.py  → Central secure library          │
│  kamkrk_v2_secure.py      → WiFi/Android (simulated)        │
│  detect_secure.py         → Device detection (simulated)    │
│  networks_secure.py       → Network discovery (simulated)   │
│                                                              │
│  ✅ Input validation                                         │
│  ✅ Simulation mode                                          │
│  ✅ No real network impact                                   │
│  ✅ Safe for training/demos                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  INSECURE (Lab Only)                        │
├─────────────────────────────────────────────────────────────┤
│  kamkrk_v2.py             → Real WiFi operations            │
│  detect.py                → Real device operations          │
│  networks.py              → Real network operations         │
│                                                              │
│  ⚠️  Requires LAB_MODE=true                                  │
│  ⚠️  Requires written authorization                          │
│  ⚠️  Can cause real network impact                           │
│  ⚠️  Only for authorized testing                             │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
/workspace/
├── app.py                          # Main Flask application (API gateway)
├── kamkrk_v2.html                  # Frontend dashboard
│
├── SECURE MODULES (Always use)
│   ├── secure_network_tools.py     # Central secure library ⭐
│   ├── kamkrk_v2_secure.py         # WiFi/Android operations
│   ├── detect_secure.py            # Device detection
│   └── networks_secure.py          # Network discovery
│
├── INSECURE MODULES (Lab only)
│   ├── kamkrk_v2.py                # Real WiFi operations ⚠️
│   ├── detect.py                   # Real device operations ⚠️
│   └── networks.py                 # Real network operations ⚠️
│
├── SHARED MODULES
│   ├── network_interface_manager.py # Network interface handling
│   └── security_validation.py       # Security validators
│
├── TESTS
│   └── test_security.py            # Security test suite (ALWAYS run)
│
├── DEPLOYMENT
│   ├── start.sh                    # Main startup script
│   ├── start_fixed.sh              # Fixed startup variant
│   ├── auto-install.sh             # Automated installer
│   └── requirements.txt            # Python dependencies
│
├── DATABASE
│   ├── cyber_matrix.db             # SQLite database
│   └── cyber_matrix.log            # Application logs
│
├── DOCUMENTATION
│   ├── docs/
│   │   ├── AI_INSTRUCTIONS.md      # AI workflow guide ⭐
│   │   ├── project-rules.md        # Global rules ⭐
│   │   ├── general-guidelines.md   # Fallback guidelines
│   │   └── modules/
│   │       ├── backend/            # Backend-specific docs
│   │       ├── frontend/           # Frontend-specific docs
│   │       ├── testing/            # Testing-specific docs
│   │       └── legacy-scripts/     # Script-specific docs
│   │
│   ├── PRD.md                      # Product Requirements Document
│   ├── README.md                   # User-facing documentation
│   ├── SECURITY_REPORT.md          # Security assessment
│   └── TROUBLESHOOTING_GUIDE.md    # Common issues
│
└── MCP CONFIGURATION
    └── .mcp/
        ├── .cursorrules            # Enhanced Cursor rules ⭐
        ├── mcp-config.json         # MCP server config ⭐
        ├── PROJECT_KNOWLEDGE_BASE.md # This file
        └── (other MCP files)
```

---

## 🔒 Security Architecture

### Default Security Posture

**CRITICAL**: The project defaults to MAXIMUM SECURITY:

1. **Simulation Mode**: All operations return simulated results
2. **Input Validation**: All user inputs validated before processing
3. **No Real Network Impact**: Safe for demos and training
4. **Authentication Required**: API endpoints protected with @require_api_key
5. **Rate Limited**: Flask-Limiter prevents abuse
6. **Audit Logging**: All operations logged to cyber_matrix.log

### Security Levels

```
Level 1: SIMULATION (Default)
├── All network operations simulated
├── No real packets sent
├── Safe for public demos
└── Educational use only

Level 2: LAB_MODE (Requires explicit authorization)
├── Real network operations enabled
├── Requires LAB_MODE=true environment variable
├── Requires written authorization to test network
├── Should bind to 127.0.0.1 only
└── Full audit logging mandatory
```

### Dangerous Patterns (NEVER allow)

```python
# ❌ NEVER use shell=True
subprocess.call(cmd, shell=True)  # PROHIBITED

# ❌ NEVER use eval/exec with user input
eval(user_input)  # PROHIBITED

# ❌ NEVER disable authentication
@app.route('/api/sensitive')  # Missing @require_api_key - PROHIBITED

# ❌ NEVER bind to 0.0.0.0 without proxy
app.run(host='0.0.0.0')  # DANGEROUS - use 127.0.0.1

# ❌ NEVER enable debug in production
app.run(debug=True)  # DANGEROUS - use debug=False
```

### Safe Patterns (ALWAYS use)

```python
# ✅ Use secure module
from secure_network_tools import simulate_network_scan
result = simulate_network_scan(target)

# ✅ Validate input
import ipaddress
try:
    ipaddress.ip_address(user_input)
    # Safe to proceed
except ValueError:
    return error_response("Invalid IP")

# ✅ Require authentication
@app.route('/api/secure', methods=['POST'])
@require_api_key
def secure_endpoint():
    pass

# ✅ Use safe subprocess
subprocess.run(['command', 'arg'], shell=False, timeout=30)

# ✅ Check LAB_MODE
LAB_MODE = os.environ.get('LAB_MODE', 'false').lower() == 'true'
if LAB_MODE and authorized():
    # Real operation
else:
    # Simulation (default)
```

---

## 🎨 Frontend Architecture

### Technology Stack

- **HTML5 + Tailwind CSS** (via CDN)
- **Vanilla JavaScript** (no framework)
- **Chart.js** for data visualization
- **Fetch API** for backend communication

### UI Structure

```
kamkrk_v2.html
├── Header
│   ├── Title: "CYBER-MATRIX v8.0"
│   └── Subtitle: "HOLOGRAPHIC PENETRATION SUITE"
│
├── Main Dashboard
│   ├── Network Scanner Panel
│   ├── Port Scanner Panel
│   ├── Vulnerability Scanner Panel
│   └── Attack Dashboard Panel
│
├── Metrics Section
│   ├── Security Metrics Card
│   ├── Network Activity Card
│   └── Performance Metrics Card
│
├── Charts Section
│   ├── Scan Results Chart (Line)
│   ├── Port Status Chart (Bar)
│   ├── Vulnerability Distribution (Radar)
│   └── System Metrics Timeline (Line)
│
└── Console Output Panel
    └── Real-time log display
```

### Design System

**Color Palette**:
- Primary: Purple (`#8b5cf6`, `#a78bfa`)
- Secondary: Blue (`#3b82f6`, `#60a5fa`)
- Accent: Cyan (`#06b6d4`, `#22d3ee`)
- Background: Dark (`#0f172a`, `#1e293b`)
- Text: Light (`#f8fafc`, `#e2e8f0`)

**CSS Framework**:
- Tailwind CSS via CDN
- Custom cyberpunk gradient classes
- Matrix rain effect in background
- Glassmorphism cards

### API Integration Pattern

```javascript
// Standard API call pattern
async function scanNetwork() {
    try {
        const response = await fetch('/api/network/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': getApiKey()
            },
            body: JSON.stringify({
                interface: selectedInterface,
                range: ipRange
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        showError(error.message);
        logToConsole(`Error: ${error.message}`);
    }
}

// Polling pattern for real-time updates
setInterval(() => {
    fetchSystemMetrics();
}, 5000);  // 5-second intervals
```

---

## 🔧 Backend Architecture

### Flask Application Structure

```python
app.py (Main Application)
├── Configuration
│   ├── Flask app initialization
│   ├── CORS configuration
│   ├── Rate limiting setup
│   └── Database initialization
│
├── System Endpoints
│   ├── GET  /                          # Serve dashboard
│   ├── GET  /api/system/metrics        # Current metrics
│   └── GET  /api/system/metrics/history # Historical data
│
├── Network Operations
│   ├── POST /api/network/scan          # Network discovery
│   ├── GET  /api/network/devices       # List devices
│   ├── POST /api/port/scan             # Port scanning
│   └── POST /api/vulnerability/scan    # Vuln assessment
│
├── Charts API
│   ├── GET  /api/charts/scan_results
│   ├── GET  /api/charts/port_status
│   ├── GET  /api/charts/vulnerability
│   └── GET  /api/charts/system_metrics
│
└── Dangerous Endpoints (Disabled by default)
    ├── POST /api/console/execute       # Command execution ⚠️
    ├── POST /api/attack/hydra          # Brute force ⚠️
    └── POST /api/attack/metasploit     # Exploits ⚠️
```

### Module Organization

**secure_network_tools.py** (Central Secure Library)
```python
Functions:
├── validate_ip_address(ip)
├── validate_port_range(start, end)
├── sanitize_input(user_input)
├── simulate_network_scan(target)
├── simulate_port_scan(target, ports)
├── simulate_vulnerability_scan(target)
└── safe_subprocess_call(cmd, timeout)
```

**Networks Module** (Secure vs Insecure)
```
networks_secure.py (USE THIS):
├── discover_networks() → Simulated results
├── get_local_ip() → Safe IP detection
├── get_router_info() → Simulated router data
└── scan_network_range() → Simulated scan

networks.py (LAB ONLY):
├── discover_networks() → Real scapy operations
├── scan_network_range() → Real network scanning
└── (All functions require LAB_MODE verification)
```

### Database Schema

```sql
-- cyber_matrix.db structure

TABLE scans (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    scan_type TEXT,  -- 'network', 'port', 'vulnerability'
    target TEXT,
    status TEXT,     -- 'pending', 'running', 'completed', 'failed'
    results TEXT,    -- JSON string
    duration REAL
)

TABLE logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    level TEXT,      -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    module TEXT,
    message TEXT,
    user TEXT,
    ip_address TEXT
)

TABLE devices (
    id INTEGER PRIMARY KEY,
    ip_address TEXT,
    mac_address TEXT,
    hostname TEXT,
    first_seen TEXT,
    last_seen TEXT,
    device_type TEXT,
    os_guess TEXT
)
```

---

## 📊 API Contracts

### Request/Response Patterns

#### Network Scan

**Request**:
```json
POST /api/network/scan
{
    "interface": "eth0",
    "range": "192.168.1.0/24",
    "scan_type": "quick"
}
```

**Response**:
```json
{
    "status": "success",
    "scan_id": "scan_20251014_123456",
    "timestamp": "2025-10-14T12:34:56Z",
    "devices_found": 15,
    "devices": [
        {
            "ip": "192.168.1.10",
            "mac": "00:11:22:33:44:55",
            "hostname": "device1.local",
            "open_ports": [22, 80, 443]
        }
    ]
}
```

#### Port Scan

**Request**:
```json
POST /api/port/scan
{
    "target": "192.168.1.10",
    "ports": "1-1000",
    "scan_type": "tcp"
}
```

**Response**:
```json
{
    "status": "success",
    "target": "192.168.1.10",
    "scan_duration": 45.2,
    "open_ports": [
        {"port": 22, "service": "ssh", "version": "OpenSSH 8.2"},
        {"port": 80, "service": "http", "version": "nginx 1.18"},
        {"port": 443, "service": "https", "version": "nginx 1.18"}
    ],
    "closed_ports": 997
}
```

#### Vulnerability Scan

**Request**:
```json
POST /api/vulnerability/scan
{
    "target": "192.168.1.10",
    "intensity": "medium",
    "categories": ["cve", "config", "auth"]
}
```

**Response**:
```json
{
    "status": "success",
    "vulnerabilities": [
        {
            "severity": "high",
            "cve": "CVE-2021-XXXXX",
            "description": "Remote code execution vulnerability",
            "affected_service": "ssh",
            "recommendation": "Update to version 8.4 or later"
        }
    ],
    "summary": {
        "critical": 0,
        "high": 1,
        "medium": 3,
        "low": 5,
        "info": 12
    }
}
```

---

## 🧪 Testing Strategy

### Test Files

```
test_security.py
├── Input Validation Tests
│   ├── test_ip_validation()
│   ├── test_port_validation()
│   └── test_input_sanitization()
│
├── Security Constraint Tests
│   ├── test_no_shell_true()
│   ├── test_authentication_required()
│   └── test_rate_limiting()
│
├── Module Safety Tests
│   ├── test_secure_modules_default()
│   └── test_lab_mode_enforcement()
│
└── Integration Tests
    ├── test_api_endpoints()
    └── test_database_operations()
```

### Running Tests

```bash
# Run all security tests (MANDATORY before commit)
python3 test_security.py

# Run with verbose output
python3 test_security.py -v

# Run specific test
python3 test_security.py TestInputValidation.test_ip_validation
```

### Test Requirements

All new features MUST have:
1. ✅ Input validation tests
2. ✅ Security constraint tests
3. ✅ Error handling tests
4. ✅ Integration tests
5. ✅ >80% code coverage

---

## 🚀 Deployment Configuration

### Environment Variables

```bash
# Security Configuration
LAB_MODE=false              # Never true in production
DEBUG=false                 # Never true in production
SECRET_KEY=<random-secret>  # Strong random key

# Network Configuration
FLASK_HOST=127.0.0.1       # Never 0.0.0.0 without proxy
FLASK_PORT=5000
ALLOWED_ORIGINS=http://localhost:5000

# Database Configuration
DB_PATH=cyber_matrix.db
DB_BACKUP_ENABLED=true
DB_BACKUP_INTERVAL=3600

# API Configuration
API_KEY_REQUIRED=true
RATE_LIMIT_PER_MINUTE=60
MAX_SCAN_TARGETS=256

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=cyber_matrix.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30
```

### Startup Checks

```bash
# start.sh performs these checks:
1. ✅ Verify Python 3.7+ installed
2. ✅ Check required dependencies
3. ✅ Verify database exists or create it
4. ✅ Check DEBUG=false for production
5. ✅ Verify LAB_MODE=false by default
6. ✅ Check FLASK_HOST=127.0.0.1
7. ✅ Run test_security.py
8. ✅ Start application if all checks pass
```

---

## 📚 Documentation Hierarchy

### Priority Order (Critical)

```
1. docs/project-rules.md          # HIGHEST AUTHORITY
   ↓
2. docs/modules/{module}/         # Module-specific rules
   {module}-rules.md
   ↓
3. docs/general-guidelines.md     # Fallback guidelines
```

### Module Documentation Structure

Each module has three files:

1. **{module}-rules.md**: Mandatory requirements and constraints
2. **{module}-memories.md**: Important facts and context
3. **{module}-checklist.md**: Verification items

**Example for Backend**:
- `docs/modules/backend/backend-rules.md` → What MUST be done
- `docs/modules/backend/backend-memories.md` → What to remember
- `docs/modules/backend/backend-checklist.md` → How to verify

---

## 🔄 Common Workflows

### Workflow 1: Adding New API Endpoint

```
1. Read docs/modules/backend/backend-rules.md
2. Search codebase for similar endpoints (@app.route patterns)
3. Plan implementation using sequential-thinking MCP
4. Implement with:
   - @require_api_key decorator
   - Input validation
   - Rate limiting
   - Error handling
   - Secure module usage
5. Add tests to test_security.py
6. Run python3 test_security.py
7. Update docs/modules/backend/backend-memories.md
8. Git diff to review changes
9. Commit with descriptive message
```

### Workflow 2: Fixing Security Issue

```
1. Read SECURITY_REPORT.md to understand context
2. Search codebase for vulnerability pattern
3. Read docs/project-rules.md for security requirements
4. Plan fix using sequential-thinking MCP
5. Implement fix using secure patterns
6. Run test_security.py to verify fix
7. Add regression test
8. Git diff to ensure minimal changes
9. Update SECURITY_REPORT.md
10. Commit with security fix tag
```

### Workflow 3: Frontend UI Update

```
1. Read docs/modules/frontend/frontend-rules.md
2. Search kamkrk_v2.html for similar UI patterns
3. Maintain cyberpunk design consistency
4. Connect to real API endpoints (not mock data)
5. Add error handling
6. Test in browser
7. Git diff to review changes
8. Commit
```

---

## 🎯 Quick Reference: Key Facts

### Most Important Files

1. **docs/AI_INSTRUCTIONS.md** → Read FIRST for any task
2. **docs/project-rules.md** → Global rules (highest authority)
3. **secure_network_tools.py** → Use for all network operations
4. **app.py** → Main Flask application
5. **test_security.py** → Run before every commit

### Most Important Rules

1. **ALWAYS use secure modules by default**
2. **NEVER use shell=True**
3. **ALWAYS validate user input**
4. **ALWAYS require authentication**
5. **ALWAYS run test_security.py before committing**

### Most Important Patterns

```python
# Import secure module
from secure_network_tools import simulate_network_scan

# Validate input
import ipaddress
ipaddress.ip_address(user_input)  # Raises ValueError if invalid

# Require authentication
@app.route('/api/endpoint')
@require_api_key
def endpoint():
    pass

# Safe subprocess
subprocess.run(['cmd', 'arg'], shell=False, timeout=30)

# Check LAB_MODE
LAB_MODE = os.environ.get('LAB_MODE', 'false').lower() == 'true'
```

---

## 🚨 Red Flags to Watch For

### Code Review Checklist

When reviewing code (use filesystem MCP to search):

```
❌ shell=True anywhere in code
❌ eval() or exec() with user input
❌ subprocess without timeout
❌ Missing @require_api_key on sensitive endpoints
❌ Hardcoded credentials or API keys
❌ DEBUG=True in deployment scripts
❌ FLASK_HOST=0.0.0.0 without proxy
❌ Unvalidated user input
❌ Import from insecure modules (networks.py, detect.py, kamkrk_v2.py)
❌ Missing error handling
❌ Disabled rate limiting
❌ Mock data in production frontend
```

---

## 📊 Metrics and KPIs

### Code Quality Standards

- **Test Coverage**: >80% for security-critical code
- **Security Tests**: 100% passing required for commits
- **Linting**: PEP 8 compliance
- **Documentation**: All public functions documented
- **Comments**: Complex logic explained

### Performance Standards

- **API Response Time**: <500ms for most endpoints
- **Scan Performance**: Network scan <30s for /24
- **Database Queries**: <100ms for simple queries
- **Frontend Load Time**: <2s initial load
- **Memory Usage**: <512MB for typical operation

---

## 🔐 Security Contact Information

### Reporting Security Issues

1. **DO NOT** open public GitHub issues for security vulnerabilities
2. Contact security team via secure channel
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if available)

### Security Review Process

1. All commits require security test passing
2. Backend changes require security review
3. New endpoints require authentication verification
4. Deployment changes require infrastructure review

---

**This knowledge base is the source of truth for AI-assisted development.**

**Use filesystem MCP to read this file at the start of each session.**

**Refer back to specific sections as needed during development.**
