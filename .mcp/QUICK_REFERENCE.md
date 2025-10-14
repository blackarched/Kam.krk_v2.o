# MCP Quick Reference Card - CYBER-MATRIX v8.0

## 🚀 Essential Commands (Copy & Use)

### 📚 Read Documentation

```
# Read AI instructions
filesystem MCP: read_file("docs/AI_INSTRUCTIONS.md")

# Read project rules (HIGHEST PRIORITY)
filesystem MCP: read_file("docs/project-rules.md")

# Read backend rules
filesystem MCP: read_file("docs/modules/backend/backend-rules.md")

# Read frontend rules
filesystem MCP: read_file("docs/modules/frontend/frontend-rules.md")

# Read security workflow
filesystem MCP: read_file(".mcp/SECURITY_WORKFLOW.md")

# Read knowledge base
filesystem MCP: read_file(".mcp/PROJECT_KNOWLEDGE_BASE.md")
```

### 🔍 Search Codebase

```
# Find security violations
filesystem MCP: search_files("shell=True", "**/*.py")
filesystem MCP: search_files("eval\\(|exec\\(", "**/*.py")

# Find authentication patterns
filesystem MCP: search_files("@require_api_key", "**/*.py")

# Find all API endpoints
filesystem MCP: search_files("@app.route", "**/*.py")

# Find secure module usage
filesystem MCP: search_files("from secure_network_tools", "**/*.py")

# Find insecure imports
filesystem MCP: search_files("from networks import|from detect import", "**/*.py")
```

### 🔄 Git Operations

```
# Check status
git MCP: git_status()

# Review changes
git MCP: git_diff()

# View history
git MCP: git_log(limit=10)

# Show specific commit
git MCP: git_show("{commit_hash}")

# Check specific file history
git MCP: git_log(path="app.py")
```

### 🧠 Remember Decisions

```
# Store security decision
memory MCP: create_memory("Security: All network operations use simulation mode by default")

# Store validation pattern
memory MCP: create_memory("Validation: IP addresses validated with ipaddress.ip_address()")

# Store implementation pattern
memory MCP: create_memory("Pattern: All API endpoints require @require_api_key decorator")

# Search memories
memory MCP: search_memories("authentication")
memory MCP: search_memories("validation pattern")
```

### 💾 Database Queries

```
# List all tables
sqlite MCP: list_tables()

# Describe table structure
sqlite MCP: describe_table("scans")
sqlite MCP: describe_table("logs")

# Query recent scans
sqlite MCP: query("SELECT * FROM scans ORDER BY timestamp DESC LIMIT 10")

# Query error logs
sqlite MCP: query("SELECT * FROM logs WHERE level='ERROR' ORDER BY timestamp DESC")

# Count records
sqlite MCP: query("SELECT COUNT(*) as total FROM scans")
```

### 🤔 Plan Complex Changes

```
# Use sequential thinking for complex refactoring
sequential-thinking MCP: create_sequential_thinking("Plan migration from insecure to secure modules")

# Use sequential thinking for security architecture
sequential-thinking MCP: create_sequential_thinking("Design authentication system with RBAC")

# Use sequential thinking for feature planning
sequential-thinking MCP: create_sequential_thinking("Plan implementation of new scan type")
```

---

## 🔒 Security Cheat Sheet

### ALWAYS Use These Patterns

```python
# ✅ Secure module import
from secure_network_tools import simulate_network_scan

# ✅ Input validation
import ipaddress
try:
    ipaddress.ip_address(user_input)
except ValueError:
    return jsonify({'error': 'Invalid IP'}), 400

# ✅ Authentication
@app.route('/api/endpoint', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def secure_endpoint():
    pass

# ✅ Safe subprocess
subprocess.run(['cmd', 'arg'], shell=False, timeout=30)

# ✅ LAB_MODE check
LAB_MODE = os.environ.get('LAB_MODE', 'false').lower() == 'true'
if LAB_MODE:
    result = real_operation()
else:
    result = simulate_operation()  # DEFAULT
```

### NEVER Use These Patterns

```python
# ❌ shell=True
subprocess.call(cmd, shell=True)

# ❌ eval/exec with user input
eval(user_input)

# ❌ Missing authentication
@app.route('/api/sensitive')
def unprotected():
    pass

# ❌ Insecure imports
from networks import discover_networks

# ❌ No input validation
@app.route('/api/scan', methods=['POST'])
def scan():
    target = request.json.get('target')
    scan(target)  # DANGEROUS - no validation
```

---

## 📋 Pre-Commit Checklist

```
□ Read documentation (filesystem MCP)
□ Search for shell=True (filesystem MCP)
□ Search for eval/exec (filesystem MCP)
□ Check git diff (git MCP)
□ Verify secure module usage
□ Validate all inputs
□ Require authentication
□ Run python3 test_security.py
□ Remember decisions (memory MCP)
```

---

## 🎯 Common Workflows

### Workflow 1: Add New API Endpoint

```
1. filesystem MCP: read_file("docs/modules/backend/backend-rules.md")
2. filesystem MCP: search_files("@app.route", "**/*.py")
3. sequential-thinking MCP: plan implementation
4. Implement with:
   - @require_api_key
   - Input validation
   - Secure module usage
5. git MCP: git_diff()
6. Run: python3 test_security.py
7. memory MCP: store pattern
```

### Workflow 2: Fix Security Issue

```
1. filesystem MCP: search for vulnerability pattern
2. git MCP: git_log(path="vulnerable_file.py")
3. filesystem MCP: read_file("docs/project-rules.md")
4. sequential-thinking MCP: plan fix
5. Implement using secure patterns
6. Run: python3 test_security.py
7. git MCP: git_diff()
```

### Workflow 3: Refactor to Secure Module

```
1. filesystem MCP: read current file
2. filesystem MCP: read secure_network_tools.py
3. sequential-thinking MCP: plan migration
4. Replace insecure imports with secure
5. Add LAB_MODE checks
6. git MCP: git_diff()
7. Run: python3 test_security.py
```

---

## 📁 Key Files

### Must Read First
- `docs/AI_INSTRUCTIONS.md` ⭐
- `docs/project-rules.md` ⭐
- `.mcp/PROJECT_KNOWLEDGE_BASE.md` ⭐

### Security Critical
- `secure_network_tools.py` (use this!)
- `test_security.py` (run before commit)
- `.mcp/SECURITY_WORKFLOW.md`

### Module Documentation
- `docs/modules/backend/backend-rules.md`
- `docs/modules/frontend/frontend-rules.md`
- `docs/modules/testing/testing-rules.md`

### Main Application
- `app.py` (Flask backend)
- `kamkrk_v2.html` (Frontend dashboard)

---

## 🎨 Module Quick Reference

### Secure Modules (ALWAYS USE)
| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `secure_network_tools.py` | Central secure library | `simulate_network_scan()`, `validate_ip_address()` |
| `networks_secure.py` | Network discovery | `discover_networks()`, `get_local_ip()` |
| `detect_secure.py` | Device detection | `detect_devices()` |
| `kamkrk_v2_secure.py` | WiFi operations | `simulate_wifi_scan()` |

### Insecure Modules (LAB ONLY)
| Module | Requires | Warning |
|--------|----------|---------|
| `networks.py` | LAB_MODE=true | Real network operations |
| `detect.py` | LAB_MODE=true | Real device operations |
| `kamkrk_v2.py` | LAB_MODE=true | Real WiFi operations |

---

## 🔧 Input Validation Patterns

```python
# IP Address
import ipaddress
ipaddress.ip_address(user_input)  # Raises ValueError if invalid

# IP Range
ipaddress.ip_network(user_input, strict=False)

# Port Number
def validate_port(port):
    return 1 <= int(port) <= 65535

# String Sanitization
import re
sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '', user_input)
```

---

## 🚨 Emergency Commands

### If Security Test Fails

```bash
# Run with verbose output
python3 test_security.py -v

# Run specific test
python3 test_security.py TestInputValidation

# Check what changed
git diff

# Revert changes if needed
git checkout -- filename.py
```

### If Found shell=True

```
1. filesystem MCP: search_files("shell=True", "**/*.py")
2. For each occurrence:
   - Read file context
   - Refactor to use shell=False with list
   - Add input validation
3. Run: python3 test_security.py
```

### If Found Insecure Import

```
1. filesystem MCP: read the file
2. filesystem MCP: read secure alternative
3. Replace import
4. Update function calls
5. Run: python3 test_security.py
```

---

## 📊 Status Check Commands

### Quick Project Status

```
# See what's changed
git MCP: git_status()

# Review changes
git MCP: git_diff()

# Check database
sqlite MCP: list_tables()

# Recent activity
sqlite MCP: query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10")
```

### Health Checks

```bash
# Security tests
python3 test_security.py

# Quick security scan
grep -r "shell=True" *.py
grep -rE "eval\(|exec\(" *.py

# Check secure module usage
grep -r "from secure_network_tools" *.py
```

---

## 🎯 Priority Order (ALWAYS FOLLOW)

```
1. docs/project-rules.md          (HIGHEST AUTHORITY)
2. docs/modules/{module}/*-rules.md   (Module specific)
3. docs/general-guidelines.md     (Fallback)
```

---

## 💡 Pro Tips

### Efficiency Tips

1. **Batch MCP operations**: Read multiple files in one request
2. **Use memory MCP**: Don't repeat context gathering
3. **Sequential thinking**: Plan before coding
4. **Git diff often**: Catch issues early

### Security Tips

1. **Default to secure modules**: Always
2. **Validate everything**: Never trust user input
3. **Require auth**: Protect all sensitive endpoints
4. **Test before commit**: Run test_security.py
5. **LAB_MODE check**: For any real network operation

### Documentation Tips

1. **Read first**: Never skip documentation
2. **Follow priority**: project-rules.md > module rules > general
3. **Update docs**: When adding new patterns
4. **Use templates**: From PROMPT_TEMPLATES.md

---

## 🔗 Related Files

### MCP Configuration
- `.mcp/.cursorrules` - Enhanced Cursor rules
- `.mcp/mcp-config.json` - MCP server config
- `.mcp/PROJECT_KNOWLEDGE_BASE.md` - Complete project knowledge
- `.mcp/PROMPT_TEMPLATES.md` - Ready-to-use prompts
- `.mcp/SECURITY_WORKFLOW.md` - Security validation workflow

### Documentation
- `docs/AI_INSTRUCTIONS.md` - AI workflow guide
- `docs/project-rules.md` - Global rules
- `docs/modules/backend/` - Backend docs
- `docs/modules/frontend/` - Frontend docs

### Code
- `app.py` - Main Flask app
- `secure_network_tools.py` - Secure library
- `test_security.py` - Security tests

---

## 📞 Quick Help

### "I need to..."

| Task | Start With |
|------|-----------|
| Add new feature | Read: `docs/modules/{module}/{module}-rules.md` |
| Fix bug | Search: `filesystem MCP: search_files("{error}")` |
| Review security | Read: `.mcp/SECURITY_WORKFLOW.md` |
| Understand project | Read: `.mcp/PROJECT_KNOWLEDGE_BASE.md` |
| Use MCP effectively | Read: `.mcp/PROMPT_TEMPLATES.md` |
| Before committing | Run: `python3 test_security.py` |

### "I'm not sure..."

| Question | Answer |
|----------|--------|
| Which module to use? | Always use `*_secure.py` variants |
| How to validate input? | Use `ipaddress` module for IPs, range checks for ports |
| Need authentication? | Yes, use `@require_api_key` decorator |
| Can I use shell=True? | NO - Always use `shell=False` |
| LAB_MODE enabled? | Check: `os.environ.get('LAB_MODE', 'false')` |

---

## 🎓 Learning Path

### New to Project

```
Day 1:
1. Read: .mcp/PROJECT_KNOWLEDGE_BASE.md
2. Read: docs/AI_INSTRUCTIONS.md
3. Read: docs/project-rules.md
4. Explore: filesystem MCP to browse code

Day 2:
5. Read: docs/modules/backend/backend-rules.md
6. Read: .mcp/SECURITY_WORKFLOW.md
7. Practice: Use MCP to search patterns
8. Try: Add simple endpoint following patterns

Day 3:
9. Read: .mcp/PROMPT_TEMPLATES.md
10. Use: Templates for common tasks
11. Practice: Pre-commit workflow
12. Master: Security validation
```

---

## 🚀 Power User Commands

### Advanced MCP Combinations

```
# Complete context gathering
1. filesystem MCP: read_file("docs/AI_INSTRUCTIONS.md")
2. filesystem MCP: search_files("similar_pattern", "**/*.py")
3. git MCP: git_log(limit=5, path="relevant_file")
4. sequential-thinking MCP: plan implementation
5. memory MCP: store decisions

# Security deep dive
1. git MCP: git_diff()
2. filesystem MCP: search_files("shell=True", "**/*.py")
3. filesystem MCP: search_files("@require_api_key", "**/*.py")
4. sqlite MCP: query("SELECT * FROM logs WHERE level='ERROR'")
5. Run: python3 test_security.py

# Database investigation
1. sqlite MCP: list_tables()
2. sqlite MCP: describe_table("scans")
3. sqlite MCP: query("SELECT * FROM scans ORDER BY timestamp DESC LIMIT 5")
4. filesystem MCP: search_files("scans.*INSERT", "**/*.py")
```

---

## 🎯 Most Common Mistakes to Avoid

```
❌ Not reading documentation first
✅ Always read docs/AI_INSTRUCTIONS.md

❌ Using insecure modules
✅ Always use *_secure.py variants

❌ Missing input validation
✅ Validate all user inputs

❌ Forgetting authentication
✅ Add @require_api_key to endpoints

❌ Using shell=True
✅ Use shell=False with command list

❌ Not running tests
✅ Run python3 test_security.py before commit

❌ Skipping git diff review
✅ Review git diff before committing

❌ Not using MCP servers
✅ Leverage filesystem/git/memory/sequential-thinking
```

---

## ⚡ One-Liner Commands

```bash
# Quick security check
python3 test_security.py && echo "✅ Safe to commit" || echo "❌ Fix issues first"

# Find all endpoints
grep -r "@app.route" *.py

# Find security violations
grep -r "shell=True" *.py && echo "❌ Found violations" || echo "✅ Clean"

# Count secure module usage
grep -c "from secure_network_tools" *.py
```

---

## 📝 Template: Quick Start Any Task

```
# Step 1: Read context
filesystem MCP: read_file("docs/AI_INSTRUCTIONS.md")
filesystem MCP: read_file("docs/modules/{module}/{module}-rules.md")

# Step 2: Search patterns
filesystem MCP: search_files("{relevant_pattern}", "**/*.py")

# Step 3: Plan
sequential-thinking MCP: plan implementation with security focus

# Step 4: Implement
[Write code following secure patterns]

# Step 5: Validate
git MCP: git_diff()
Run: python3 test_security.py

# Step 6: Remember
memory MCP: create_memory("Decision: {what you decided and why}")
```

---

**Print this reference card for quick access during development!**

**All commands are designed for immediate copy-paste use.**

**When in doubt, prioritize security and documentation.**
