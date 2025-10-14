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

# legacy-scripts-memories
- These scripts contain known command injection vulnerabilities.
- They frequently use `shell=True` with unsanitized user input.
- `kamkrk_v2.py` contains insecure Wi-Fi attack functions.
- `detect.py` contains insecure device detection logic.
- `networks.py` contains insecure network discovery methods.
- Their secure replacements are the `*_secure.py` files.
- All their intended functionality is now in `app.py` via secure modules.
- These files are preserved for historical or educational context only.
- They lack proper input validation and error handling.
- They depend on external tools being in the system's PATH.
