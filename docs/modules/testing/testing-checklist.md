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

# testing-checklist
- The main security test suite `test_security.py` exists and is executable.
- The `security_validation.py` script can be run to check for code issues.
- Tests cover input validation for IP addresses and port ranges.
- Tests verify that command injection attempts are handled safely.
- The test suite checks that sensitive API endpoints require authentication.
- Tests confirm that `shell=True` is not used in secure modules.
- The testing setup is documented in the project's README or contributing guide.
- CI/CD pipeline is configured to run all tests on new commits.
