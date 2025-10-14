# legacy-scripts-checklist
- Verify these scripts are not imported or called by the main `app.py`.
- Confirm no running processes are associated with these scripts.
- Ensure their functionality is fully replaced by the `*_secure.py` modules.
- Check that project documentation marks these files as deprecated.
- Confirm they are excluded from any production build or deployment process.
- Ensure they are not executable by default (`chmod -x`).
- Verify that `secure_network_tools.py` is used as the replacement library.
- Check that no new code adds dependencies on these legacy files.
- Confirm they are not included in the test suite execution.