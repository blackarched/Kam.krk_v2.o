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