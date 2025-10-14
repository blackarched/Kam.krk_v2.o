# Automated Security Validation Workflow with MCP

## 🎯 Purpose

This document defines automated security validation workflows using MCP servers. These workflows ensure that every code change maintains the project's security posture before committing.

---

## 🚨 Pre-Commit Security Validation (MANDATORY)

### Complete Workflow

Every commit MUST pass this validation sequence:

```
┌────────────────────────────────────────────────────────┐
│ Step 1: Check Git Status                              │
│ Use: git MCP → git_status()                           │
│ Purpose: Identify all modified files                  │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 2: Review All Changes                            │
│ Use: git MCP → git_diff()                             │
│ Purpose: See exactly what code is being committed     │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 3: Search for Dangerous Patterns                 │
│ Use: filesystem MCP → search_files()                  │
│ Patterns:                                             │
│   - "shell=True"                                      │
│   - "eval\\(" or "exec\\("                           │
│   - "subprocess\\.(call|run|Popen)"                  │
│   - Hardcoded credentials                            │
│   - Missing @require_api_key                         │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 4: Verify Secure Module Usage                    │
│ Use: filesystem MCP → read modified files             │
│ Check:                                                │
│   - Imports from secure_network_tools.py ✅          │
│   - Imports from *_secure.py files ✅                │
│   - No imports from insecure variants ❌             │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 5: Validate Input Handling                       │
│ Use: filesystem MCP → read modified endpoints         │
│ Check:                                                │
│   - All user inputs validated                        │
│   - IP addresses use ipaddress module                │
│   - Port numbers checked for range                   │
│   - String inputs sanitized                          │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 6: Check Authentication & Rate Limiting          │
│ Use: filesystem MCP → search modified files           │
│ Check:                                                │
│   - New endpoints have @require_api_key              │
│   - Rate limiting configured                         │
│   - Proper error responses (don't leak info)         │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 7: Read Module Documentation                     │
│ Use: filesystem MCP → read relevant docs             │
│ Files:                                                │
│   - docs/modules/{module}/{module}-rules.md          │
│   - docs/modules/{module}/{module}-checklist.md      │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 8: Run Security Test Suite                       │
│ Command: python3 test_security.py                    │
│ Must Pass: 100% of security tests                    │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 9: Remember Security Decisions                   │
│ Use: memory MCP → create_memory()                    │
│ Store:                                                │
│   - Security patterns used                           │
│   - Validation approaches                            │
│   - Important decisions                              │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│ Step 10: Final Verification                           │
│ Use: git MCP → git_diff() once more                  │
│ Verify: Changes match intended modifications         │
└────────────────────────────────────────────────────────┘
                        ↓
                   ✅ SAFE TO COMMIT
```

---

## 🔍 Detailed Security Checks

### Check 1: Dangerous Shell Execution

**Purpose**: Prevent command injection vulnerabilities

**MCP Commands**:
```
Use filesystem MCP:
search_files("shell=True", "**/*.py")
search_files("shell\\s*=\\s*True", "**/*.py")
```

**What to look for**:
- ❌ `subprocess.call(cmd, shell=True)`
- ❌ `subprocess.run(cmd, shell=True)`
- ❌ `subprocess.Popen(cmd, shell=True)`
- ❌ `os.system(cmd)`

**Remediation**:
```python
# ❌ NEVER DO THIS
import subprocess
subprocess.call(user_input, shell=True)  # DANGEROUS!

# ✅ ALWAYS DO THIS
import subprocess
subprocess.run(['command', 'arg1', 'arg2'], 
               shell=False, 
               timeout=30,
               capture_output=True)
```

**If found**:
1. Identify the file and line number
2. Read surrounding context with filesystem MCP
3. Refactor to use shell=False with command list
4. Add input validation if user input involved
5. Re-run security checks

---

### Check 2: Code Injection Vulnerabilities

**Purpose**: Prevent code execution attacks

**MCP Commands**:
```
Use filesystem MCP:
search_files("eval\\(", "**/*.py")
search_files("exec\\(", "**/*.py")
search_files("__import__\\(", "**/*.py")
```

**What to look for**:
- ❌ `eval(user_input)`
- ❌ `exec(user_input)`
- ❌ `compile(user_input, ...)`
- ❌ `__import__(user_input)`

**Remediation**:
```python
# ❌ NEVER DO THIS
user_code = request.json.get('code')
eval(user_code)  # EXTREMELY DANGEROUS!

# ✅ IF YOU MUST EVALUATE (rarely needed)
import ast
try:
    tree = ast.parse(user_code, mode='eval')
    # Validate tree only contains safe nodes
    # Use restricted evaluation
except SyntaxError:
    return error_response("Invalid syntax")
```

**If found**:
1. Determine if eval/exec is absolutely necessary
2. 99% of the time, there's a safer alternative
3. If truly needed, use AST parsing and validation
4. Add extensive input validation
5. Consider using a sandbox environment

---

### Check 3: Missing Authentication

**Purpose**: Ensure all sensitive endpoints require authentication

**MCP Commands**:
```
Use filesystem MCP:
1. search_files("@app.route", "**/*.py")
2. For each endpoint, check for "@require_api_key" decorator
```

**What to look for**:
```python
# ❌ MISSING AUTHENTICATION
@app.route('/api/sensitive/data', methods=['GET'])
def sensitive_endpoint():
    # Returns sensitive data without auth check
    pass

# ✅ PROPERLY AUTHENTICATED
@app.route('/api/sensitive/data', methods=['GET'])
@require_api_key
@limiter.limit("10 per minute")
def sensitive_endpoint():
    # Protected endpoint
    pass
```

**Endpoint Security Levels**:
```
Public (No Auth Required):
- GET / (dashboard)
- GET /health
- GET /api/status

Protected (Auth Required):
- ALL /api/* endpoints (except status)
- ALL POST/PUT/DELETE operations
- ALL admin operations

Forbidden (Never Expose):
- /api/console/execute (unless LAB_MODE)
- /api/attack/* (unless LAB_MODE)
```

**If missing authentication**:
1. Add @require_api_key decorator
2. Add rate limiting with appropriate limits
3. Add input validation
4. Add audit logging
5. Update API documentation

---

### Check 4: Insecure Module Imports

**Purpose**: Ensure only secure modules are used

**MCP Commands**:
```
Use filesystem MCP:
search_files("from networks import", "**/*.py")
search_files("from detect import", "**/*.py")
search_files("from kamkrk_v2 import", "**/*.py")
search_files("import networks[^_]", "**/*.py")
search_files("import detect[^_]", "**/*.py")
```

**What to look for**:
```python
# ❌ INSECURE IMPORTS
from networks import discover_networks
from detect import scan_devices
import kamkrk_v2

# ✅ SECURE IMPORTS
from networks_secure import discover_networks
from detect_secure import scan_devices
from secure_network_tools import simulate_network_scan
import kamkrk_v2_secure
```

**Module Mapping**:
| Insecure Module | Secure Alternative | Purpose |
|----------------|-------------------|---------|
| networks.py | networks_secure.py | Network discovery |
| detect.py | detect_secure.py | Device detection |
| kamkrk_v2.py | kamkrk_v2_secure.py | WiFi operations |
| (direct subprocess) | secure_network_tools.py | Command execution |

**If insecure imports found**:
1. Identify which functions are being imported
2. Use filesystem MCP to read the secure alternative
3. Replace with secure equivalent functions
4. Add LAB_MODE check if real operation needed
5. Update tests

---

### Check 5: Input Validation

**Purpose**: Ensure all user inputs are validated

**MCP Commands**:
```
Use filesystem MCP:
1. Read modified files
2. Find all request.json.get(), request.args.get(), request.form.get()
3. Verify validation exists for each input
```

**Validation Patterns**:
```python
# IP Address Validation
import ipaddress

def validate_ip_address(ip_string):
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        logger.warning(f"Invalid IP: {ip_string}")
        return False

# Port Number Validation
def validate_port(port):
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False

# IP Range Validation
def validate_ip_range(range_string):
    try:
        ipaddress.ip_network(range_string, strict=False)
        return True
    except ValueError:
        return False

# String Sanitization
import re

def sanitize_string(user_input, max_length=100):
    # Remove any characters that aren't alphanumeric, dash, underscore, or dot
    sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '', user_input)
    return sanitized[:max_length]
```

**Required Validations by Input Type**:
| Input Type | Validation Required |
|-----------|-------------------|
| IP Address | ipaddress.ip_address() |
| IP Range | ipaddress.ip_network() |
| Port Number | 1 <= port <= 65535 |
| Port Range | Validate both start and end |
| Interface Name | Whitelist of known interfaces |
| File Path | Restrict to allowed directories |
| URL | urllib.parse validation |
| Any string | Sanitize special characters |

**If validation missing**:
1. Identify input type
2. Add appropriate validation function
3. Return 400 Bad Request for invalid input
4. Log validation failures
5. Add test case for invalid input

---

### Check 6: LAB_MODE Enforcement

**Purpose**: Ensure dangerous operations check LAB_MODE

**MCP Commands**:
```
Use filesystem MCP:
search_files("LAB_MODE", "**/*.py")
```

**Required Pattern**:
```python
import os

LAB_MODE = os.environ.get('LAB_MODE', 'false').lower() == 'true'

def potentially_dangerous_operation(target):
    """
    Performs network operation - REQUIRES LAB_MODE for real execution
    """
    if LAB_MODE and user_has_authorization():
        logger.warning(f"LAB_MODE: Performing real operation on {target}")
        # Real operation
        result = real_network_scan(target)
    else:
        # ALWAYS default to simulation
        logger.info(f"SIMULATION: Simulating operation on {target}")
        result = simulate_network_scan(target)
    
    return result
```

**Operations requiring LAB_MODE check**:
- Network scanning with real packets
- Port scanning real targets
- WiFi deauthentication
- Password cracking attempts
- Exploit execution
- Any operation affecting real networks

**If LAB_MODE check missing**:
1. Add LAB_MODE environment variable check
2. Default to simulation mode
3. Require explicit authorization for real operations
4. Add prominent warning logs for real operations
5. Update documentation

---

### Check 7: Hardcoded Secrets

**Purpose**: Prevent credential leaks

**MCP Commands**:
```
Use filesystem MCP:
search_files("password.*=.*['\"]", "**/*.py")
search_files("api_key.*=.*['\"]", "**/*.py")
search_files("secret.*=.*['\"]", "**/*.py")
search_files("token.*=.*['\"]", "**/*.py")
```

**What to look for**:
```python
# ❌ HARDCODED SECRETS
API_KEY = "abc123secret456"
PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret"

# ✅ ENVIRONMENT VARIABLES
import os
API_KEY = os.environ.get('API_KEY')
PASSWORD = os.environ.get('DB_PASSWORD')
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
```

**Common Secret Patterns to Catch**:
- `password = "..."`
- `api_key = "..."`
- `secret = "..."`
- `token = "..."`
- `aws_access_key = "..."`
- `private_key = "..."`

**If secrets found**:
1. Remove hardcoded value
2. Use environment variable
3. Add to .env.example (with dummy value)
4. Update .gitignore to exclude .env
5. Update documentation
6. If already committed, rotate the secret

---

### Check 8: Configuration Security

**Purpose**: Verify secure configuration defaults

**MCP Commands**:
```
Use filesystem MCP:
1. Read start.sh
2. Read app.py
3. Search for DEBUG, HOST, LAB_MODE settings
```

**Required Secure Defaults**:
```bash
# ✅ SECURE DEFAULTS
export DEBUG=False
export FLASK_HOST=127.0.0.1
export LAB_MODE=false
export SECRET_KEY=$(python3 -c "import os; print(os.urandom(24).hex())")
```

```python
# ✅ SECURE APP CONFIGURATION
app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['HOST'] = os.environ.get('FLASK_HOST', '127.0.0.1')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
```

**Configuration Security Checklist**:
- [ ] DEBUG=False (never True in production)
- [ ] HOST=127.0.0.1 (never 0.0.0.0 without proxy)
- [ ] LAB_MODE=false (never True by default)
- [ ] Strong SECRET_KEY (random, not hardcoded)
- [ ] HTTPS enforced (if not behind proxy)
- [ ] Secure headers configured (via Flask-Talisman)
- [ ] CORS properly restricted
- [ ] Rate limiting enabled

**If insecure configuration**:
1. Update to secure defaults
2. Add runtime validation
3. Fail startup if insecure
4. Document required configuration
5. Add to security test suite

---

## 🧪 Automated Test Execution

### Security Test Suite

**Location**: `test_security.py`

**Must run before every commit**:
```bash
python3 test_security.py
```

**Expected output**:
```
Running security tests...
✅ test_ip_validation_valid ........................... PASS
✅ test_ip_validation_invalid ......................... PASS
✅ test_port_validation ............................... PASS
✅ test_no_shell_true ................................. PASS
✅ test_secure_modules_imported ....................... PASS
✅ test_authentication_required ....................... PASS
✅ test_rate_limiting_configured ...................... PASS
✅ test_input_sanitization ............................ PASS
✅ test_lab_mode_enforcement .......................... PASS
✅ test_no_hardcoded_secrets .......................... PASS

All tests passed! ✅
```

**If any test fails**:
```
❌ STOP - Do not commit
1. Read test failure details
2. Fix the underlying issue
3. Re-run tests
4. Only commit when all tests pass
```

---

## 💾 Security Decision Memory

### Using Memory MCP

**Store important security decisions**:
```
Use memory MCP: create_memory()

Examples:
- "Security decision: All network scans use simulation mode by default"
- "Validation pattern: IP addresses validated with ipaddress.ip_address()"
- "Authentication pattern: All /api/* endpoints require @require_api_key"
- "LAB_MODE check added to all network operations in commit abc123"
```

**Retrieve security patterns**:
```
Use memory MCP: search_memories("authentication pattern")
Use memory MCP: search_memories("validation for IP")
Use memory MCP: search_memories("LAB_MODE decision")
```

**Benefits**:
- Consistency across development sessions
- Remember why decisions were made
- Share patterns with team
- Avoid repeating security mistakes

---

## 📋 Complete Pre-Commit Checklist

Copy this checklist for every commit:

```
Pre-Commit Security Validation Checklist
─────────────────────────────────────────────────────────

□ Step 1: Git Status
  ├─ Used git MCP to check status
  └─ Reviewed all modified files

□ Step 2: Git Diff
  ├─ Used git MCP to review all changes
  └─ Verified changes match intentions

□ Step 3: Dangerous Patterns
  ├─ Searched for "shell=True" (filesystem MCP)
  ├─ Searched for "eval(" or "exec(" (filesystem MCP)
  ├─ Searched for unprotected subprocess calls
  └─ NO dangerous patterns found

□ Step 4: Secure Modules
  ├─ Checked imports use *_secure.py variants
  ├─ Verified secure_network_tools.py usage
  └─ NO insecure module imports

□ Step 5: Input Validation
  ├─ All user inputs validated
  ├─ IP addresses use ipaddress module
  ├─ Ports checked for valid range
  └─ Strings sanitized

□ Step 6: Authentication
  ├─ New endpoints have @require_api_key
  ├─ Rate limiting configured
  └─ Error handling doesn't leak info

□ Step 7: LAB_MODE
  ├─ Dangerous operations check LAB_MODE
  ├─ Default to simulation mode
  └─ Real operations logged prominently

□ Step 8: Configuration
  ├─ DEBUG=False in production
  ├─ HOST=127.0.0.1
  ├─ No hardcoded secrets
  └─ Secure defaults enforced

□ Step 9: Tests
  ├─ Ran python3 test_security.py
  ├─ All tests passed
  └─ Added tests for new features

□ Step 10: Documentation
  ├─ Read relevant module rules (filesystem MCP)
  ├─ Followed documented patterns
  ├─ Updated documentation if needed
  └─ Remembered decisions (memory MCP)

─────────────────────────────────────────────────────────
✅ ALL CHECKS PASSED - SAFE TO COMMIT
```

---

## 🚀 Quick Security Check Commands

### One-Line Security Audit

```
Quick security check before commit:

python3 -c "
import subprocess
import sys

checks = [
    ('shell=True check', 'grep -r \"shell=True\" *.py'),
    ('eval/exec check', 'grep -rE \"eval\\(|exec\\(\" *.py'),
    ('hardcoded secrets', 'grep -rE \"password.*=.*[\\'\\\"]|api_key.*=.*[\\'\\\"]\" *.py'),
]

failed = []
for name, cmd in checks:
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        print(f'❌ {name}: Issues found')
        failed.append(name)
    else:
        print(f'✅ {name}: Clean')

if failed:
    print(f'\\n❌ Failed checks: {failed}')
    sys.exit(1)
else:
    print('\\n✅ All quick checks passed')
    sys.exit(0)
"
```

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

echo "Running pre-commit security checks..."

# Run security tests
python3 test_security.py
if [ $? -ne 0 ]; then
    echo "❌ Security tests failed - commit aborted"
    exit 1
fi

# Check for dangerous patterns
if grep -r "shell=True" *.py; then
    echo "❌ Found shell=True in code - commit aborted"
    exit 1
fi

echo "✅ Pre-commit checks passed"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📊 Security Metrics

### Track Security Over Time

**Metrics to monitor**:
```
Use sqlite MCP to track:
1. Number of security tests
2. Test pass rate
3. Security issues found per commit
4. Average time to fix security issues
5. Number of security-related commits
```

**Sample Queries**:
```sql
-- Security-related commits
SELECT COUNT(*) FROM logs 
WHERE message LIKE '%security%' 
AND timestamp > date('now', '-30 days');

-- Failed security tests
SELECT COUNT(*) FROM logs 
WHERE level='ERROR' AND module='test_security'
AND timestamp > date('now', '-7 days');
```

---

## 🎯 Integration with CI/CD

### GitHub Actions Workflow

```yaml
name: Security Tests

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run security tests
        run: python3 test_security.py
      - name: Check for dangerous patterns
        run: |
          ! grep -r "shell=True" *.py
          ! grep -rE "eval\\(|exec\\(" *.py
```

---

**This workflow ensures security is maintained at every commit.**

**Use MCP servers to automate these checks efficiently.**

**Security is not optional - it's mandatory for every change.**
