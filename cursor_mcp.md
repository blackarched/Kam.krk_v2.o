You are an advanced MCP infrastructure engineer operating inside Cursor.
Your task is to fully build, configure, orchestrate, and harden a multi-agent MCP server environment for this project.
This MCP environment is editor-only — it assists development inside Cursor and does not modify runtime behavior of the production project.

The environment must support:
• Automated task splitting and routing between multiple agents.
• Mandatory doc-rule enforcement before every action.
• Secure local execution.
• Self-healing recovery if any agent fails.


---

1. Rule Enforcement Foundation

Before performing any setup or action:

Read and apply all markdown rules located in docs/.

Required files include but are not limited to:

docs/mcp-rules.md

docs/frontend-rules.md

docs/backend-rules.md

docs/attack-rules.md

docs/general-guidelines.md


If any critical file is missing or unreadable, abort setup immediately.




---

2. Project Structure Setup

Create the following directory structure:

mcp/
  config/
  bin/
  register/
  exec/
  test/
  recovery/
  output/
agents/
logs/
ci/

This structure is mandatory and must align with markdown rules.


---

3. Agent Creation

Create and configure 3 specialized MCP agents:

1. frontend-agent → handles UI, visual layers, 3D map, interface updates.


2. backend-agent → handles server-side logic, endpoints, data handling.


3. attack-agent → handles network & device discovery, attack functionality, and related tasks.



Each config file in mcp/config must include:

{
  "name": "frontend-agent",
  "role": "frontend",
  "allowedPaths": ["src/frontend", "docs/frontend-rules.md"],
  "readDocs": ["docs/frontend-rules.md", "docs/general-guidelines.md"],
  "mcpEndpoint": 7010,
  "auth": { "token": "REPLACE_ME_TOKEN" }
}

Adjust for backend-agent and attack-agent accordingly.


---

4. Core MCP Server Script

Create mcp/server.js to:

Load config for each agent.

Serve:

GET /health

GET /info

POST /task (enforces doc-reading + allowed paths).


Require valid tokens.

Bind strictly to 127.0.0.1.


Create mcp/bin/run-mcp-servers.sh to launch all agents in parallel with logging.


---

5. Orchestration Layer

Create agents/orchestrator.js to:

Monitor agent health and uptime.

Detect conflicts and failed agents.

Restart agents on failure.

Log orchestration events to logs/orchestrator.log.



---

6. Automatic Registration with Cursor

Create mcp/register/cursor-register.sh that generates:

{
  "frontend-agent": "http://127.0.0.1:7010",
  "backend-agent": "http://127.0.0.1:7011",
  "attack-agent": "http://127.0.0.1:7012"
}

Ensure Cursor auto-detects and connects to these endpoints on load.


---

7. Auto Task Splitting

The Cursor assistant must:

Analyze each incoming task.

Route or split tasks intelligently between the three MCP agents based on their roles.

Execute tasks in parallel when applicable.

Coordinate shared operations between agents (e.g., backend feeds data → frontend renders).



Example:
“Update the network visualization with live device discovery” →
• Frontend rendering → frontend-agent
• API integration → backend-agent
• Discovery logic → attack-agent


---

8. Security Hardening

Bind all MCP servers to 127.0.0.1 only.

Require valid tokens (no default allowed).

Enforce strict allowedPaths.

Refuse to execute any task if required docs are unread.



---

9. Recovery System (Self-Healing)

Create a recovery layer in mcp/recovery/:

mcp/recovery/restart-agent.sh

Monitors each agent’s health via /health.

If an agent fails, restarts it immediately.

Logs the incident to logs/recovery.log.


mcp/recovery/auto-heal.js

Triggers restart script.

Revalidates doc rules after restart.

Resyncs agent registration with Cursor.


Orchestrator must call recovery automatically if any agent is unresponsive.


Agents should return to operational state without user input.


---

10. Testing & CI

Create:

mcp/test/test-mcp-servers.sh:

Start servers.

Run health checks.

Test task routing.

Simulate agent failure → ensure recovery works.


ci/validate-mcp.yml:

Run tests on commit or push.

Fail CI if any agent or recovery check fails.




---

11. Verification Run

After setup:

bash mcp/bin/run-mcp-servers.sh
curl -s http://127.0.0.1:7010/health
curl -s http://127.0.0.1:7011/health
curl -s http://127.0.0.1:7012/health
bash mcp/test/test-mcp-servers.sh

Logs:

logs/orchestrator.log
logs/recovery.log
mcp/output/test-results.json


---

12. Strict Assistant Behavior

Cursor’s AI assistant must:

Always read relevant markdown rule files before task execution.

Split and route tasks to correct MCP agents automatically.

Reject tasks outside allowed paths or without doc reference.

Auto-recover MCP agents if they fail mid-task.

Log task assignments and outcomes.




---

✅ Final Outcome:

3 fully operational MCP agents specialized by role.

Automatic task splitting and parallel execution in Cursor.

Mandatory markdown rule enforcement.

Localhost-only secure environment.

Self-healing recovery if any agent fails.

Full testing and logging infrastructure.
