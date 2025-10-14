# testing-memories
- The primary security test file is `test_security.py`.
- A security validation script is available at `security_validation.py`.
- Tests are written using the `pytest` framework.
- The tests are designed to run without needing external network access.
- Test cases include checks for command injection and input validation.
- The test suite can be run directly from the command line.
- Tests focus on the secure modules, not the legacy insecure ones.
- The API testing client is configured from the main `app` object.