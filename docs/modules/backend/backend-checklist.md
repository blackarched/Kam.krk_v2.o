<!-- AI ASSISTANT INSTRUCTION:
This file contains critical rules and instructions.
Any AI assistant (Cursor, VS Code Copilot, etc.) must fully read and apply the contents of this file
before making any modifications or generating code related to its scope.
Priority order if multiple files apply:
1. docs/project-rules.md
2. Relevant module-specific file
3. docs/general-guidelines.md
No task should be executed without referencing the correct documentation first.
-->

# backend-checklist
- Main application file `app.py` serves the frontend and all APIs.
- All API endpoints are decorated with `@require_api_key`.
- Database operations use parameterized queries to prevent SQL injection.
- Secure tools from `secure_network_tools.py` are used for OS commands.
- The app binds to `127.0.0.1` by default for security.
- Asynchronous tasks like network scans run in a background thread.
- Error handling is applied to all API routes to prevent information leaks.
- Rate limiting is active on sensitive or intensive endpoints.
- Input validation is performed on all data from requests.
- The `network_interface_manager.py` handles all interface controls.
