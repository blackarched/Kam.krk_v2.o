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

# deployment-memories
- The main installation script is `auto-install-enhanced.sh`.
- A quick start script `start.sh` is provided for manual launch.
- A secure deployment script `deploy_secure.sh` is also available.
- Scripts support Ubuntu, Debian, CentOS, RHEL, Fedora, Arch, and openSUSE.
- The installer creates a Python virtual environment at `./venv`.
- The scripts handle system package manager updates and installations.
- The application is started on `http://127.0.0.1:5000` by default.
- The installer provides user-friendly error handling and recovery options.
- Systemd service hardening is included in the enhanced installer.
- A suite of CLI tools named `cyber-matrix` is created by the installer.
