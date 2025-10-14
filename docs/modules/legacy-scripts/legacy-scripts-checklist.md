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

# legacy-scripts-checklist
- Verify these scripts are not imported or called by the main `app.py`.
- Confirm no running processes are associated with these scripts.
- Ensure their functionality is fully replaced by the `*_secure.py` modules.
- Check that project documentation marks these files as deprecated.
- Confirm they are excluded from any production build or deployment process.
- Ensure they are not executable by default (`chmod -x`).
- Verify that `secure_network_tools.py` is used as the replacement library.
- Check that no new code adds dependencies on these legacy files.
- Confirm they are not included in the test suite execution.
