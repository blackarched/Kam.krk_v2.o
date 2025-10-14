# 📋 Copy-Paste Ready MCP Installation Guide

**For CYBER-MATRIX v8.0 - Complete in 5 Minutes**

This is your one-stop, copy-paste ready guide. Each section contains exact commands you can copy and run.

---

## 🚀 PART 1: One-Command Installation

### Copy and run this:

```bash
bash .mcp/install-mcp-servers.sh
```

This installs all 8 MCP servers automatically.

---

## 🔧 PART 2: Manual Installation (If Automated Fails)

### For macOS/Linux:

```bash
# Install Node.js-based MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-sqlite

# Install Python MCP server
pip3 install mcp-server-python
```

### For Windows (PowerShell):

```powershell
# Install Node.js-based MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-sqlite

# Install Python MCP server
pip install mcp-server-python
```

---

## 📝 PART 3: Copy Configuration to IDE

### For Cursor on macOS:

```bash
# Create directory
mkdir -p "$HOME/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings"

# Copy config
cp .mcp/mcp-config.json "$HOME/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
```

### For Cursor on Linux:

```bash
# Create directory
mkdir -p "$HOME/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings"

# Copy config
cp .mcp/mcp-config.json "$HOME/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
```

### For Cursor on Windows (PowerShell):

```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings"

# Copy config
Copy-Item .mcp\mcp-config.json "$env:APPDATA\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json"
```

### For VS Code (any OS):

Replace `Cursor` with `Code` in the paths above.

---

## 🔑 PART 4: Optional API Tokens

### GitHub Token (Optional but Recommended):

1. **Get token:** https://github.com/settings/tokens/new
2. **Select scopes:** `repo`, `read:org`, `read:user`
3. **Copy the token**
4. **Edit `.env.mcp`:**

```bash
nano .env.mcp  # or use any text editor
```

5. **Replace this line:**
```
GITHUB_TOKEN=your_github_token_here
```

**With:**
```
GITHUB_TOKEN=ghp_your_actual_token_from_github
```

### Brave Search API Key (Optional):

1. **Get key:** https://brave.com/search/api/
2. **Sign up for free tier**
3. **Edit `.env.mcp`:**

```bash
nano .env.mcp
```

4. **Replace this line:**
```
BRAVE_API_KEY=your_brave_api_key_here
```

**With:**
```
BRAVE_API_KEY=your_actual_brave_api_key
```

---

## ✅ PART 5: Verify Installation

### Copy and run:

```bash
bash .mcp/verify-mcp.sh
```

**Expected output:**
- ✓ All servers installed
- ✓ Configuration files present
- ✓ IDE config detected

---

## 🔄 PART 6: Restart IDE

**IMPORTANT:** You MUST completely restart your IDE.

### macOS/Linux:
1. Quit Cursor/VS Code completely (Cmd+Q or Ctrl+Q)
2. Relaunch it

### Windows:
1. Close Cursor/VS Code completely
2. End any remaining processes in Task Manager
3. Relaunch it

---

## 🧪 PART 7: Test in IDE

### Open chat with AI and paste this:

```
List all available MCP servers and their tools
```

### Expected response should include:

- ✅ filesystem (read_file, write_file, search_files...)
- ✅ git (git_status, git_diff, git_log...)
- ✅ memory (create_memory, search_memories...)
- ✅ sequential-thinking (create_sequential_thinking...)
- ✅ sqlite (query, list_tables...)
- ✅ python (execute_python...)
- ⚙️ github (if token configured)
- ⚙️ brave-search (if API key configured)

---

## 🎯 PART 8: Quick Functionality Tests

### Copy and paste these one at a time:

**Test 1: Filesystem**
```
Read the file docs/AI_INSTRUCTIONS.md and tell me the three-tier priority order
```

**Test 2: Git**
```
Show me the current git status
```

**Test 3: Memory**
```
Remember: CYBER-MATRIX v8.0 uses Flask 3.1.0 and Python 3.7+
```

**Test 4: Sequential Thinking**
```
Use sequential thinking to plan how to add rate limiting to all API endpoints
```

**Test 5: Search**
```
Search all Python files for the string "secure_network_tools"
```

**Test 6: Git History**
```
Show me the last 5 commits
```

**Test 7: Database (if database exists)**
```
List all tables in cyber_matrix.db
```

**Test 8: Memory Recall**
```
What did I tell you to remember about CYBER-MATRIX?
```

---

## 🐛 TROUBLESHOOTING

### If servers don't appear:

```bash
# Check Node.js version (must be 18+)
node --version

# Check installations
npm list -g | grep modelcontextprotocol

# Verify configuration was copied
ls -la ~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/  # macOS
ls -la ~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/  # Linux
dir "%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\"  # Windows
```

### If filesystem server fails:

**Edit the config file and update paths:**

macOS/Linux:
```bash
# Find npx path
which npx

# Find your workspace path
pwd
```

Windows:
```powershell
# Find npx path
where.exe npx

# Find your workspace path
cd
```

**Then edit the config file and replace:**
- `"npx"` with the full path from `which npx` or `where.exe npx`
- `"/workspace"` with your actual project path

### If git server fails:

```bash
# Ensure you're in a git repo
git status

# Ensure git is in PATH
which git  # macOS/Linux
where.exe git  # Windows
```

### If Python server fails:

```bash
# Check Python installation
python3 --version

# Check mcp-server-python
pip3 show mcp-server-python

# Reinstall if needed
pip3 install --force-reinstall mcp-server-python
```

---

## 🎉 SUCCESS CHECKLIST

After completing all steps, you should have:

- [ ] All 8 MCP servers installed (verified with `npm list -g`)
- [ ] Configuration copied to IDE
- [ ] IDE restarted completely
- [ ] MCP servers visible in chat ("List available MCP servers")
- [ ] Filesystem test passed (can read files)
- [ ] Git test passed (can show status)
- [ ] Memory test passed (can remember info)
- [ ] Sequential thinking test passed (can plan tasks)

---

## 📚 WHAT'S NEXT

### 1. Read the documentation:
```bash
# In your IDE chat:
Read .mcp/README.md and summarize the key features
```

### 2. Try a real workflow:
```
Use MCP to:
1. Read docs/AI_INSTRUCTIONS.md
2. Read docs/project-rules.md
3. Show git status
4. Remember all key security rules
5. List all Python files in the project
```

### 3. Integrate with your development:

For ANY code change, AI will now:
- ✅ Read documentation automatically
- ✅ Search codebase for patterns
- ✅ Check git history
- ✅ Remember context
- ✅ Plan implementation
- ✅ Follow project rules

---

## 🔒 SECURITY REMINDER

**Before committing:**

```bash
# Verify these files are NOT staged:
git status | grep -E '(.env.mcp|.mcp/memory)'

# They should NOT appear in git status
# If they do:
git reset .env.mcp
git reset .mcp/memory/
```

**These files contain secrets and should NEVER be committed!**

---

## 📞 NEED HELP?

### Quick fixes:

**Problem: Servers not showing**
→ **Solution:** Restart IDE completely, run verify script

**Problem: Filesystem errors**
→ **Solution:** Check workspace path in config matches `pwd`

**Problem: Git errors**
→ **Solution:** Ensure you're in a git repo (`git status`)

**Problem: GitHub/Brave errors**
→ **Solution:** Check tokens are in `.env.mcp`

### Full documentation:

- **Setup:** `.mcp/setup-guide.md`
- **Testing:** `.mcp/test-mcp-servers.md`
- **Integration:** `.mcp/integration-with-docs.md`
- **Quick Ref:** `.mcp/quick-reference.md`

### Official resources:

- **MCP Docs:** https://modelcontextprotocol.io/
- **GitHub:** https://github.com/modelcontextprotocol/servers
- **Issues:** https://github.com/modelcontextprotocol/servers/issues

---

## 🚀 YOU'RE DONE!

Your CYBER-MATRIX v8.0 IDE is now supercharged!

**Total setup time:** ~5 minutes  
**Result:** 10x more productive development  
**Integration:** Complete documentation control + MCP automation

### Start using it right now:

```
Help me add a new API endpoint for real-time network monitoring. 
Use MCP to read the relevant documentation and plan the implementation.
```

The AI will:
1. Read `docs/AI_INSTRUCTIONS.md`
2. Read `docs/modules/backend/backend-rules.md`
3. Search for similar API endpoint patterns
4. Plan the implementation step-by-step
5. Follow all security requirements
6. Remember the implementation decisions

**Happy coding with MCP! 🎉**

---

*Copy-Paste Installation Guide v1.0*  
*Complete setup in 5 minutes*  
*For CYBER-MATRIX v8.0*
