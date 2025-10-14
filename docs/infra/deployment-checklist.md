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

# deployment-checklist
- Verify `auto-install-enhanced.sh` is present and executable.
- Confirm the script successfully installs all system dependencies.
- Check that the Python virtual environment is created and activated.
- Ensure `pip install -r requirements.txt` completes without errors.
- Verify the script can set up the application as a systemd service.
- Confirm the `start.sh` script successfully launches the web server.
- Check that the application is accessible at the default URL after install.
- Verify the installer provides a secure API key upon completion.
- Confirm that deployment scripts bind the app to `127.0.0.1` by default.
- Check that installation logs are created for troubleshooting.
