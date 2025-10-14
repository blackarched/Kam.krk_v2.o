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

# legacy-scripts-rules
- Do not run these scripts in any production environment.
- Replace all usage of these scripts with their secure alternatives.
- Use these scripts for security vulnerability analysis only.
- Remove any `shell=True` calls if you must modify them for testing.
- Sanitize all inputs before passing them to any function in these files.
- Assume these scripts contain critical and unpatched security flaws.
- Delete these files entirely after migrating to the secure versions.
- Do not add any new features or code to these files.
- Prevent these files from being executed by web server processes.
- Educate developers about the specific risks these files pose.
