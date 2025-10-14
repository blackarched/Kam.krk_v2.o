# MCP Server Configuration for CYBER-MATRIX v8.0

## 📚 Quick Links

- **[Setup Guide](setup-guide.md)** - Complete installation and configuration instructions
- **[Configuration File](mcp-config.json)** - Ready-to-use MCP configuration
- **[Testing Guide](test-mcp-servers.md)** - Verify all servers are working
- **[Installation Script](install-mcp-servers.sh)** - Automated installation

---

## 🎯 What is MCP?

Model Context Protocol (MCP) is a standardized protocol that allows AI assistants in your IDE (Cursor, VS Code) to access external tools and services. This dramatically enhances the capabilities of your AI coding assistant.

### Why MCP for CYBER-MATRIX v8.0?

MCP servers provide:
- **Filesystem operations** - Batch file reading, searching, editing
- **Git integration** - Commit history, diffs, branch management
- **GitHub integration** - Issue tracking, PR management
- **Web search** - Find documentation and solutions
- **Memory** - Remember project context across sessions
- **Database access** - Query and inspect SQLite databases
- **Python execution** - Run scripts and validate code
- **Sequential thinking** - Break down complex refactoring tasks

---

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# From project root
bash .mcp/install-mcp-servers.sh
```

Follow the prompts and instructions.

### Option 2: Manual Installation

1. **Install MCP servers:**
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-git
   npm install -g @modelcontextprotocol/server-github
   npm install -g @modelcontextprotocol/server-brave-search
   npm install -g @modelcontextprotocol/server-memory
   npm install -g @modelcontextprotocol/server-sequential-thinking
   npm install -g @modelcontextprotocol/server-sqlite
   pip install mcp-server-python
   ```

2. **Copy configuration:**
   - Copy `.mcp/mcp-config.json` to your IDE's MCP settings location
   - Update paths for your system

3. **Configure environment:**
   - Create `.env.mcp` with your API tokens
   - Set GITHUB_TOKEN and BRAVE_API_KEY

4. **Restart IDE**

5. **Test:**
   - Follow [Testing Guide](test-mcp-servers.md)

---

## 📁 Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This file - overview and quick start |
| `setup-guide.md` | Detailed setup instructions |
| `mcp-config.json` | MCP server configuration (copy to IDE) |
| `install-mcp-servers.sh` | Automated installation script |
| `test-mcp-servers.md` | Testing procedures for each server |
| `memory/` | Storage for MCP memory server (auto-created) |

---

## 🔧 Configured MCP Servers

### Core Servers (Always Enabled)

| Server | Tools | Use Cases |
|--------|-------|-----------|
| **filesystem** | read_file, write_file, search_files, list_directory | Read docs, search code, batch operations |
| **git** | git_status, git_diff, git_log, git_commit | Version control, commit history, code review |
| **memory** | create_memory, search_memories, get_memory | Remember project context, decisions, patterns |
| **sequential-thinking** | create_sequential_thinking | Break down complex refactoring, planning |

### Optional Servers (Require API Keys)

| Server | Requirements | Use Cases |
|--------|--------------|-----------|
| **github** | GitHub token | Issue management, PR review, repo stats |
| **brave-search** | Brave API key | Documentation lookup, solution search, security advisories |

### Utility Servers

| Server | Requirements | Use Cases |
|--------|--------------|-----------|
| **sqlite** | Database file exists | Inspect cyber_matrix.db, query data, check schema |
| **python** | Python 3, mcp-server-python | Run scripts, validate security, execute tests |

---

## 🎓 Common Workflows

### 1. Reading Project Documentation

```
Read docs/AI_INSTRUCTIONS.md and summarize the key rules
```

The AI will use the filesystem server to read and analyze the file.

### 2. Checking Git History

```
Show me the last 10 commits and identify any security-related changes
```

The AI will use git server to retrieve and analyze commit history.

### 3. Searching for Security Issues

```
Search all Python files for uses of shell=True
```

The AI will use filesystem server to search the codebase.

### 4. Planning Complex Changes

```
Use sequential thinking to plan how to add authentication middleware to all API endpoints
```

The AI will break down the task into logical steps.

### 5. Querying Database

```
Show me the structure of cyber_matrix.db and query recent scan results
```

The AI will use SQLite server to inspect and query the database.

### 6. Finding Documentation

```
Search for "Flask CSRF protection best practices"
```

The AI will use Brave search to find relevant documentation (if configured).

### 7. Remembering Project Context

```
Remember: All network operations must use secure_network_tools.py
```

Later sessions:
```
What are the rules about network operations?
```

The AI will recall the stored memory.

---

## 🔒 Security Considerations

### What MCP Servers Can Do

✅ **Safe operations:**
- Read files in workspace
- Search code
- Query git history
- Store/retrieve memories
- Execute read-only database queries

⚠️ **Operations requiring confirmation:**
- Write/modify files
- Delete files
- Git commits (auto-approved)
- Git push (requires confirmation)
- Database writes

### What MCP Servers Cannot Do

❌ **Prevented operations:**
- Access files outside workspace
- Execute system commands arbitrarily
- Access network without permission
- Modify .git directory directly
- Execute unsafe Python code

### API Key Security

**IMPORTANT:**
- Never commit `.env.mcp` to git
- Store tokens securely
- Use minimal permission scopes
- Rotate tokens regularly
- Review token usage in GitHub settings

---

## 🐛 Troubleshooting

### Servers Not Appearing

1. Verify Node.js 18+ installed
2. Check npm global installation
3. Restart IDE completely
4. Check IDE MCP settings location
5. Verify JSON syntax in config file

### Filesystem Server Issues

- Confirm workspace path is correct
- Check file permissions
- Verify excluded paths are correct

### Git Server Issues

- Ensure you're in a git repository
- Verify git is installed and in PATH
- Check repository permissions

### GitHub Server Issues

- Verify GITHUB_TOKEN is set
- Check token has correct scopes
- Test token with curl

### Python Server Issues

- Confirm Python 3 is installed
- Verify mcp-server-python is installed
- Check PYTHONPATH includes workspace

See [Testing Guide](test-mcp-servers.md) for detailed troubleshooting.

---

## 📈 Advanced Usage

### Custom MCP Workflows

Create project-specific MCP workflows:

**Security Audit Workflow:**
```
1. Search for "shell=True" in all Python files
2. Check git log for security-related commits
3. Review docs/security/ for compliance
4. Query database for security events
```

**Documentation Update Workflow:**
```
1. Read relevant documentation files
2. Check what changed in recent commits
3. Update documentation accordingly
4. Validate with docs:check script
```

**Refactoring Workflow:**
```
1. Use sequential thinking to plan changes
2. Search codebase for affected files
3. Remember refactoring decisions
4. Validate with tests before committing
```

### Integration with Project Documentation

MCP servers automatically reference:
- `docs/AI_INSTRUCTIONS.md` for coding standards
- `docs/project-rules.md` for global rules
- `docs/general-guidelines.md` for best practices

The AI will check these before making changes.

---

## 🔄 Maintenance

### Updating MCP Servers

```bash
# Update all Node.js servers
npm update -g @modelcontextprotocol/server-filesystem
npm update -g @modelcontextprotocol/server-git
npm update -g @modelcontextprotocol/server-github
npm update -g @modelcontextprotocol/server-brave-search
npm update -g @modelcontextprotocol/server-memory
npm update -g @modelcontextprotocol/server-sequential-thinking
npm update -g @modelcontextprotocol/server-sqlite

# Update Python server
pip install --upgrade mcp-server-python
```

### Clearing Memory Server

```bash
# Clear all memories
rm -rf .mcp/memory/*

# Clear specific memories
rm .mcp/memory/<memory-id>.json
```

### Resetting Configuration

```bash
# Backup current config
cp .mcp/mcp-config.json .mcp/mcp-config.backup.json

# Reset to default
cp .mcp/mcp-config.json.template .mcp/mcp-config.json
```

---

## 📞 Getting Help

- **MCP Documentation:** https://modelcontextprotocol.io/
- **GitHub Issues:** https://github.com/modelcontextprotocol/servers/issues
- **Project Documentation:** `docs/AI_INSTRUCTIONS.md`
- **Setup Issues:** See `setup-guide.md` troubleshooting section

---

## ✅ Next Steps

After setting up MCP servers:

1. ✅ Complete [Setup Guide](setup-guide.md)
2. ✅ Run [Testing Guide](test-mcp-servers.md)
3. ✅ Configure API tokens in `.env.mcp`
4. ✅ Test each server individually
5. ✅ Try common workflows
6. ✅ Integrate with documentation system
7. ✅ Share configuration with team

---

**MCP Configuration Package Version 1.0**  
*Last Updated: 2025-10-14*  
*For CYBER-MATRIX v8.0*
