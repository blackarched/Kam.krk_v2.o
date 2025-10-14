# config-rules
- Pin all dependency versions in `requirements.txt`.
- Run a dependency vulnerability scan before every release.
- Remove unused dependencies from the requirements file.
- Add a comment explaining the purpose of non-obvious packages.
- Ensure the installation guide references the `requirements.txt` file.
- Separate production and development requirements if needed.
- Verify all dependencies are compatible with the target Python version.```

### **`cursor-rules/config-memories.md`**
```markdown
# config-memories
- The file for Python dependencies is `requirements.txt`.
- `Flask==3.1.0` is the core web framework version.
- `pip>=25.2` is required to patch CVE-2025-8869.
- `psutil` is used for system monitoring.
- `scapy` is listed for network packet operations.
- `Flask-Limiter` is used for API rate limiting.
- `Flask-Talisman` is available for setting security headers.
- `pytest` is the framework for running tests.