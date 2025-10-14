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

# testing-memories
- The primary security test file is `test_security.py`.
- A security validation script is available at `security_validation.py`.
- Tests are written using the `pytest` framework.
- The tests are designed to run without needing external network access.
- Test cases include checks for command injection and input validation.
- The test suite can be run directly from the command line.
- Tests focus on the secure modules, not the legacy insecure ones.
- The API testing client is configured from the main `app` object.
