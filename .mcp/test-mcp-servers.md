# MCP Server Testing Guide

## Quick Test Commands

After installing and configuring MCP servers, use these commands to verify each server is working correctly.

---

## 🧪 Test Suite

### 1. List Available MCP Tools

**Ask your AI assistant:**
```
List all available MCP servers and their tools
```

**Expected Response:**
You should see a list including:
- filesystem tools (read_file, write_file, search_files, etc.)
- git tools (git_status, git_diff, git_log, etc.)
- github tools (if configured)
- brave-search tools (if configured)
- memory tools
- sequential-thinking tools
- sqlite tools
- python tools (if configured)

---

### 2. Test Filesystem Server

**Test 1: Read a file**
```
Read the file docs/AI_INSTRUCTIONS.md
```

**Expected:** Content of AI_INSTRUCTIONS.md should be displayed

**Test 2: List directory**
```
List all markdown files in the docs/ directory
```

**Expected:** List of .md files should be displayed

**Test 3: Search files**
```
Search for "shell=True" in all Python files
```

**Expected:** List of files containing "shell=True" or confirmation none found

---

### 3. Test Git Server

**Test 1: Status**
```
Show me the current git status
```

**Expected:** Git status output (branch, modified files, etc.)

**Test 2: Log**
```
Show me the last 5 git commits
```

**Expected:** Recent commit history

**Test 3: Diff**
```
Show me the git diff for README.md
```

**Expected:** Diff output if file is modified, or "no changes" message

---

### 4. Test GitHub Server (Requires Token)

**Test 1: Repository info**
```
Get information about this GitHub repository
```

**Expected:** Repository details (if token is configured)

**Test 2: List issues**
```
List open issues for this repository
```

**Expected:** Open issues list or indication no token configured

---

### 5. Test Brave Search Server (Requires API Key)

**Test 1: Simple search**
```
Search for "Flask security best practices 2024"
```

**Expected:** Search results from Brave

**Test 2: Technical search**
```
Search for "Python subprocess security without shell=True"
```

**Expected:** Relevant search results

---

### 6. Test Memory Server

**Test 1: Create memory**
```
Remember: CYBER-MATRIX v8.0 uses secure_network_tools.py for all system commands
```

**Expected:** Confirmation memory was created

**Test 2: Search memories**
```
Search memories for "secure_network_tools"
```

**Expected:** Previously stored memory retrieved

**Test 3: Verify persistence**
- Restart IDE
- Ask: "What do you remember about secure_network_tools.py?"

**Expected:** Memory should be recalled from storage

---

### 7. Test Sequential Thinking Server

**Test 1: Complex task**
```
Use sequential thinking to plan how to add a new API endpoint for real-time network monitoring
```

**Expected:** Step-by-step breakdown of the task

**Test 2: Refactoring plan**
```
Use sequential thinking to plan how to refactor the backend to improve security
```

**Expected:** Logical sequence of refactoring steps

---

### 8. Test SQLite Server

**Test 1: List tables**
```
List all tables in cyber_matrix.db
```

**Expected:** List of database tables

**Test 2: Describe schema**
```
Describe the schema of the main table in cyber_matrix.db
```

**Expected:** Table structure with columns and types

**Test 3: Query data**
```
Query: SELECT * FROM <table_name> LIMIT 5
```

**Expected:** First 5 rows of data (or error if table doesn't exist yet)

---

### 9. Test Python Server (If Installed)

**Test 1: Simple execution**
```
Execute this Python code:
import os
print(f"Current directory: {os.getcwd()}")
print(f"Python version: {os.sys.version}")
```

**Expected:** Current directory and Python version output

**Test 2: File check**
```
Execute this Python code:
import os
files = [f for f in os.listdir('.') if f.endswith('.py')]
print(f"Python files: {files}")
```

**Expected:** List of Python files in current directory

**Test 3: Security validation**
```
Execute: python3 security_validation.py
```

**Expected:** Security validation results

---

## 🔍 Troubleshooting Tests

### If Filesystem Server Fails

**Check:**
1. Workspace path is correct in config
2. File permissions allow read access
3. npx is in PATH and working

**Debug command:**
```bash
npx -y @modelcontextprotocol/server-filesystem /workspace
```

### If Git Server Fails

**Check:**
1. You're in a git repository
2. Git is installed and in PATH
3. Repository path is correct

**Debug command:**
```bash
cd /workspace && git status
```

### If GitHub Server Fails

**Check:**
1. GITHUB_TOKEN environment variable is set
2. Token has correct scopes (repo, read:org, read:user)
3. Token is valid

**Debug command:**
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### If Brave Search Fails

**Check:**
1. BRAVE_API_KEY environment variable is set
2. API key is valid
3. You haven't exceeded rate limits

**Debug command:**
```bash
curl -H "X-Subscription-Token: $BRAVE_API_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"
```

### If Memory Server Fails

**Check:**
1. .mcp/memory directory exists
2. Directory has write permissions
3. No disk space issues

**Debug command:**
```bash
mkdir -p .mcp/memory
touch .mcp/memory/test.json
```

### If SQLite Server Fails

**Check:**
1. cyber_matrix.db file exists
2. File has read permissions
3. Database is not corrupted

**Debug command:**
```bash
sqlite3 cyber_matrix.db ".schema"
```

### If Python Server Fails

**Check:**
1. Python 3 is installed
2. mcp-server-python is installed
3. PYTHONPATH includes workspace

**Debug command:**
```bash
python3 -m mcp_server_python --version
```

---

## 🎯 Success Criteria

All tests pass when:
- ✅ All MCP servers appear in tools list
- ✅ Filesystem operations work (read, list, search)
- ✅ Git operations return valid output
- ✅ Memory persists across sessions
- ✅ Sequential thinking provides logical breakdowns
- ✅ Database queries work (if DB exists)
- ✅ No permission or path errors

Optional tests (require API keys):
- ✅ GitHub operations work with valid token
- ✅ Brave search returns results with valid key
- ✅ Python code executes successfully

---

## 📊 Test Results Tracking

Keep track of your test results:

```
[ ] Filesystem Server
    [ ] Read file
    [ ] List directory
    [ ] Search files

[ ] Git Server
    [ ] Status
    [ ] Log
    [ ] Diff

[ ] GitHub Server
    [ ] Repository info
    [ ] List issues

[ ] Brave Search Server
    [ ] Simple search
    [ ] Technical search

[ ] Memory Server
    [ ] Create memory
    [ ] Search memories
    [ ] Persistence

[ ] Sequential Thinking Server
    [ ] Complex task
    [ ] Refactoring plan

[ ] SQLite Server
    [ ] List tables
    [ ] Describe schema
    [ ] Query data

[ ] Python Server
    [ ] Simple execution
    [ ] File check
    [ ] Security validation
```

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. **Integrate with workflow:**
   - Use memory server for project context
   - Use sequential thinking for complex refactoring
   - Use brave-search for documentation lookup

2. **Optimize configuration:**
   - Disable unused servers
   - Adjust filesystem scope if needed
   - Set appropriate security policies

3. **Document project-specific patterns:**
   - Common MCP workflows
   - Frequently used tool combinations
   - Project-specific MCP commands

4. **Share with team:**
   - Ensure all developers have MCP configured
   - Document project-specific MCP usage
   - Add to onboarding documentation

---

*Testing guide version 1.0 - Last updated: 2025-10-14*
