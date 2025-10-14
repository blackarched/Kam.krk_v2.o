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

# config-rules
- Pin all dependency versions in `requirements.txt`.
- Run a dependency vulnerability scan before every release.
- Remove unused dependencies from the requirements file.
- Add a comment explaining the purpose of non-obvious packages.
- Ensure the installation guide references the `requirements.txt` file.
- Separate production and development requirements if needed.
- Verify all dependencies are compatible with the target Python version.
