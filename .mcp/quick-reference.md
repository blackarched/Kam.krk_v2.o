# MCP Quick Reference Card for CYBER-MATRIX v8.0

## 🚀 One-Line Installation

```bash
bash .mcp/install-mcp-servers.sh
```

---

## 📋 Essential Commands

### Setup
```bash
# Install all servers
npm install -g @modelcontextprotocol/server-*

# Configure environment
cp .mcp/mcp-config.json <IDE_CONFIG_PATH>

# Edit tokens
nano .env.mcp
```

### Testing
```bash
# Ask AI: "List available MCP servers"
# Ask AI: "Read docs/AI_INSTRUCTIONS.md"
# Ask AI: "Show git status"
```

---

## 🎯 Common Prompts

### Documentation
```
Read and summarize docs/AI_INSTRUCTIONS.md
```

### Code Search
```
Search for "shell=True" in all Python files
```

### Git Operations
```
Show me the last 5 commits and their changes
```

### Database Queries
```
List all tables in cyber_matrix.db
```

### Planning
```
Use sequential thinking to plan adding rate limiting to all API endpoints
```

### Memory
```
Remember: CYBER-MATRIX uses Flask 3.1.0 and requires Python 3.7+
```

---

## 🔧 Configuration Paths

### macOS
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

### Linux
```
~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

### Windows
```
%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

---

## 🎨 MCP Servers at a Glance

| Server | Key Tools | Example Use |
|--------|-----------|-------------|
| filesystem | read, write, search | `Read app.py` |
| git | status, diff, log | `Show git status` |
| github | issues, PRs | `List open issues` |
| brave-search | web_search | `Search Flask security` |
| memory | create, search | `Remember X` |
| sequential-thinking | plan | `Plan refactoring` |
| sqlite | query, schema | `Query database` |
| python | execute | `Run test_security.py` |

---

## ⚡ Workflow Examples

### Pre-Commit Check
```
1. Show git status
2. Search for any shell=True in modified files
3. Read docs/project-rules.md
4. Confirm changes follow security guidelines
```

### Adding New Feature
```
1. Read relevant module documentation
2. Use sequential thinking to plan implementation
3. Search existing code for similar patterns
4. Remember implementation decisions
5. Validate against project rules
```

### Bug Investigation
```
1. Search logs for error patterns
2. Check git log for recent related changes
3. Query database for error records
4. Search web for known issues
5. Plan fix using sequential thinking
```

---

## 🔍 Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| Servers not showing | Restart IDE, check config path |
| Filesystem errors | Verify workspace path in config |
| Git errors | Ensure you're in git repo |
| GitHub 401 error | Check GITHUB_TOKEN is set |
| Python errors | Verify mcp-server-python installed |
| Memory not persisting | Check .mcp/memory/ exists |

---

## 🔒 Security Checklist

- [ ] .env.mcp in .gitignore
- [ ] GitHub token has minimal scopes
- [ ] Filesystem limited to workspace
- [ ] Git push requires confirmation
- [ ] Database queries logged
- [ ] Python execution sandboxed

---

## 📚 More Info

- Full Setup: `.mcp/setup-guide.md`
- Testing: `.mcp/test-mcp-servers.md`
- Config: `.mcp/mcp-config.json`
- README: `.mcp/README.md`

---

*Quick Reference v1.0 - Print or keep handy!*
