# MCP Server Setup Guide for CYBER-MATRIX v8.0

## Prerequisites

Before starting, ensure you have:
- ✅ Node.js 18+ installed (`node --version`)
- ✅ npm or npx available (`npm --version`)
- ✅ Python 3.7+ installed (for Python MCP server)
- ✅ Cursor or VS Code with MCP support
- ✅ Git installed and configured

## Step-by-Step Setup

### Step 1: Verify MCP Support in Your IDE

**For Cursor:**
1. Open Cursor
2. Go to Settings → Features → Model Context Protocol
3. Verify MCP is enabled
4. Note the configuration file location (usually `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` on Mac or `%APPDATA%/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` on Windows)

**For VS Code with Claude Dev/Cline:**
1. Install the Claude Dev or Cline extension
2. Open extension settings
3. Verify MCP configuration is available

### Step 2: Install MCP Servers

Run these commands in your terminal:

```bash
# Navigate to project root
cd /path/to/cyber-matrix

# Install MCP servers globally (recommended)
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-sqlite

# For Python MCP server (requires Python)
pip install mcp-server-python
```

### Step 3: Locate Node.js Executable Path

You'll need the path to npx for the configuration:

```bash
# On macOS/Linux:
which npx
# Usually: /usr/local/bin/npx or /opt/homebrew/bin/npx

# On Windows (in PowerShell):
where.exe npx
# Usually: C:\Program Files\nodejs\npx.cmd
```

### Step 4: Get GitHub Personal Access Token (Optional but Recommended)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Generate and copy the token
5. Save it securely

### Step 5: Get Brave Search API Key (Optional)

1. Go to https://brave.com/search/api/
2. Sign up for free tier
3. Copy your API key

### Step 6: Create MCP Configuration File

The configuration file location depends on your OS and IDE:

**macOS Cursor:**
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

**Windows Cursor:**
```
%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

**Linux Cursor:**
```
~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

Create or edit this file with the configuration provided in `mcp-config.json`.

### Step 7: Set Environment Variables

Create a `.env.mcp` file in your home directory or project root:

```bash
# GitHub token (optional but recommended)
GITHUB_TOKEN=your_github_token_here

# Brave Search API key (optional)
BRAVE_API_KEY=your_brave_api_key_here

# Python path (if not in PATH)
PYTHON_PATH=/usr/bin/python3
```

**IMPORTANT:** Add `.env.mcp` to `.gitignore` to prevent committing secrets!

### Step 8: Create Project-Specific MCP Settings

In the project root, create `.mcp/project-config.json`:

```json
{
  "projectName": "CYBER-MATRIX-v8.0",
  "workspace": "/workspace",
  "allowedOperations": {
    "filesystem": {
      "readPaths": ["/workspace"],
      "writePaths": ["/workspace"],
      "excludePaths": [
        "/workspace/node_modules",
        "/workspace/__pycache__",
        "/workspace/.git",
        "/workspace/venv"
      ]
    },
    "git": {
      "allowCommit": true,
      "allowPush": false,
      "allowBranchCreate": true
    },
    "sqlite": {
      "databases": [
        "/workspace/cyber_matrix.db"
      ],
      "readOnly": false
    }
  },
  "securityRules": {
    "preventSecretsExposure": true,
    "validateBeforeCommit": true,
    "requireDocsUpdate": true
  }
}
```

### Step 9: Restart IDE

1. Close Cursor/VS Code completely
2. Reopen the project
3. MCP servers should now be available

### Step 10: Verify MCP Servers are Active

Open a chat with your AI assistant and ask:

```
Can you list available MCP servers and tools?
```

You should see responses showing filesystem, git, github, brave-search, memory, sequential-thinking, and sqlite tools.

## Testing Each MCP Server

### Test Filesystem Server
```
Please read the contents of docs/AI_INSTRUCTIONS.md
```

### Test Git Server
```
Show me the current git status and recent commits
```

### Test GitHub Server (if token configured)
```
List open issues in this repository
```

### Test Brave Search Server (if API key configured)
```
Search for "Flask security best practices 2024"
```

### Test Memory Server
```
Remember that this project uses secure_network_tools.py for all system commands
```

### Test Sequential Thinking Server
```
Use sequential thinking to plan how to add a new API endpoint for network statistics
```

### Test SQLite Server
```
Show me the schema of the cyber_matrix.db database
```

### Test Python Server
```
Execute this Python code to check if test_security.py exists:
import os
print(os.path.exists('test_security.py'))
```

## Troubleshooting

### MCP Servers Not Appearing

1. **Check Node.js version:**
   ```bash
   node --version  # Should be 18+
   ```

2. **Verify installations:**
   ```bash
   npm list -g | grep modelcontextprotocol
   ```

3. **Check configuration file syntax:**
   - Ensure JSON is valid (no trailing commas, proper quotes)
   - Use a JSON validator if needed

4. **Check permissions:**
   - Ensure npx has execute permissions
   - Verify file paths are accessible

### Specific Server Issues

**Filesystem Server:**
- Ensure workspace path is correct
- Check read/write permissions on directories

**Git Server:**
- Verify git is installed: `git --version`
- Ensure you're in a git repository

**GitHub Server:**
- Verify GitHub token has correct scopes
- Test token: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`

**SQLite Server:**
- Ensure database file exists
- Check file permissions

**Python Server:**
- Verify Python is in PATH: `python3 --version`
- Check pip installation: `pip show mcp-server-python`

### Performance Issues

If MCP servers are slow:
1. Reduce number of active servers
2. Limit filesystem server scope
3. Increase IDE memory allocation
4. Disable unused servers

## Best Practices

### Security
- ✅ Never commit tokens or API keys
- ✅ Use environment variables for secrets
- ✅ Limit filesystem access to project directory
- ✅ Set git operations to require confirmation
- ✅ Use read-only mode for production databases

### Performance
- ✅ Exclude node_modules and cache directories
- ✅ Limit search scope for filesystem operations
- ✅ Use specific paths rather than recursive searches
- ✅ Cache memory server data appropriately

### Workflow
- ✅ Use memory server to persist project context
- ✅ Use sequential thinking for complex tasks
- ✅ Leverage brave-search for documentation lookups
- ✅ Use filesystem server for batch operations

## Advanced Configuration

### Custom MCP Server

You can create custom MCP servers for project-specific needs:

```typescript
// .mcp/custom-security-checker.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const server = new Server({
  name: 'cyber-matrix-security-checker',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
  },
});

server.setRequestHandler('tools/list', async () => {
  return {
    tools: [{
      name: 'check_security',
      description: 'Run security validation on code',
      inputSchema: {
        type: 'object',
        properties: {
          file: { type: 'string' }
        }
      }
    }]
  };
});

server.connect();
```

### Integration with Documentation System

Link MCP servers with your documentation:

```json
{
  "mcp_documentation_integration": {
    "beforeCodeChange": [
      "Check docs/AI_INSTRUCTIONS.md for protocol",
      "Verify module-specific rules",
      "Confirm security requirements"
    ],
    "afterCodeChange": [
      "Update relevant documentation",
      "Run validation scripts",
      "Check for broken links"
    ]
  }
}
```

## Maintenance

### Updating MCP Servers

```bash
# Update all global MCP servers
npm update -g @modelcontextprotocol/server-filesystem
npm update -g @modelcontextprotocol/server-github
npm update -g @modelcontextprotocol/server-git
npm update -g @modelcontextprotocol/server-brave-search
npm update -g @modelcontextprotocol/server-memory
npm update -g @modelcontextprotocol/server-sequential-thinking
npm update -g @modelcontextprotocol/server-sqlite

# Update Python MCP server
pip install --upgrade mcp-server-python
```

### Monitoring

Check MCP server logs (location varies by IDE):
- Cursor: Help → Toggle Developer Tools → Console
- VS Code: View → Output → Select MCP extension

## Getting Help

- **MCP Documentation:** https://modelcontextprotocol.io/
- **GitHub Issues:** https://github.com/modelcontextprotocol/servers/issues
- **Project Documentation:** `docs/AI_INSTRUCTIONS.md`

---

*Setup guide version 1.0 - Last updated: 2025-10-14*
