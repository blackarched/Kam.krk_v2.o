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

# config-checklist
- `requirements.txt` exists and lists all necessary Python packages.
- All package versions are pinned to prevent breaking changes.
- The `pip>=25.2` requirement is present for the security fix.
- Security libraries like `Flask-Limiter` and `Flask-Talisman` are included.
- No known vulnerable packages are listed in the requirements.
- The installation scripts use `pip install -r requirements.txt`.
- Development-only packages like `pytest` are included for testing.
- The file is free of comments containing secrets or sensitive info.
