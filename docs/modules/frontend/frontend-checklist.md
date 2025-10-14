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

# frontend-checklist
- The main frontend file `kamkrk_v2.html` is served at the root URL.
- All interactive buttons are wired to the correct backend API endpoints.
- The frontend sends the API key in the `X-API-Key` header with requests.
- All charts are populated with data from the `/api/charts/*` endpoints.
- The UI gracefully handles API errors and displays feedback to the user.
- The network scanner button triggers a `POST` to `/api/network/scan`.
- The console execute button triggers a `POST` to `/api/console/execute`.
- System metrics are fetched periodically from `/api/system/metrics`.
- The interface manager correctly populates the network interface dropdown.
