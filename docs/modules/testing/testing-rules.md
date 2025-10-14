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

# testing-rules
- Run all security tests before pushing changes to the main branch.
- Add new tests for every new feature or API endpoint.
- Ensure tests cover potential security vulnerabilities like injection.
- Do not disable or skip failing security tests.
- Keep the test suite fast and reliable.
- Test for proper error handling and status codes in API responses.
- Automate the execution of the test suite in a CI pipeline.
- Regularly update tests to reflect changes in the application code.
