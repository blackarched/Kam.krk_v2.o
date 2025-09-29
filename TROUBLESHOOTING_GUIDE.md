# 🔧 CYBER-MATRIX v8.0 - Troubleshooting Guide

## 🚨 **IMMEDIATE FIXES FOR COMMON ISSUES**

### **Issue 1: "NameError: name 'app' is not defined"**
**Cause**: Import order issue in app.py
**Solution**:
```bash
# Use the fixed startup script
./start_fixed.sh

# OR manually activate virtual environment first
source venv/bin/activate
python3 app.py
```

### **Issue 2: "ModuleNotFoundError: No module named 'flask_cors'"**
**Cause**: Dependencies not installed in virtual environment
**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip>=25.2
pip install flask flask-cors psutil

# OR install all dependencies
pip install -r requirements.txt

# Then start the app
python3 app.py
```

### **Issue 3: Virtual Environment Issues**
**Cause**: Virtual environment not properly activated
**Solution**:
```bash
# Create new virtual environment
python3 -m venv venv

# Activate it (IMPORTANT!)
source venv/bin/activate

# Verify activation (should show venv path)
which python
which pip

# Install dependencies
pip install -r requirements.txt

# Start application
python3 app.py
```

---

## 🛠️ **STEP-BY-STEP PROBLEM RESOLUTION**

### **Complete Fresh Installation**
If you're having multiple issues, start fresh:

```bash
# 1. Clean up any existing installation
rm -rf venv
rm -f cyber_matrix.db cyber_matrix.log

# 2. Create new virtual environment
python3 -m venv venv

# 3. Activate virtual environment (CRITICAL STEP!)
source venv/bin/activate

# 4. Verify you're in the virtual environment
echo $VIRTUAL_ENV
# Should show path ending with /venv

# 5. Upgrade pip for security
pip install --upgrade pip>=25.2

# 6. Install core dependencies one by one
pip install flask>=3.0.0
pip install flask-cors>=4.0.0
pip install psutil>=5.9.0
pip install werkzeug>=3.0.0

# 7. Test core imports
python3 -c "import flask, flask_cors, psutil; print('✅ Core imports OK')"

# 8. Generate API key
export CYBER_MATRIX_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Your API Key: $CYBER_MATRIX_API_KEY"

# 9. Start the application
python3 app.py
```

### **Dependency Installation Issues**

#### **Problem: pip install fails**
```bash
# Update system packages first
sudo apt update
sudo apt install -y python3-dev python3-pip

# OR for CentOS/RHEL
sudo yum install -y python3-devel python3-pip

# Try installing with --user flag
pip install --user flask flask-cors psutil

# OR use system packages
sudo apt install -y python3-flask python3-psutil
```

#### **Problem: "externally-managed-environment" error**
```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR override system protection (not recommended)
pip install --break-system-packages flask flask-cors psutil
```

---

## 🔍 **DIAGNOSTIC COMMANDS**

### **Check System Status**
```bash
# Python version
python3 --version

# Virtual environment status
echo $VIRTUAL_ENV

# Installed packages
pip list

# System resources
free -h
df -h

# Network connectivity
ping -c 3 google.com
```

### **Check Application Status**
```bash
# Test imports
python3 -c "
try:
    import flask, flask_cors, psutil
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Check if port is available
netstat -tuln | grep 5000

# Check file permissions
ls -la app.py requirements.txt
```

---

## 🚀 **RECOMMENDED STARTUP PROCEDURE**

### **Every Time You Start CYBER-MATRIX:**

```bash
# 1. Navigate to project directory
cd /path/to/cyber-matrix

# 2. Activate virtual environment (ALWAYS DO THIS FIRST!)
source venv/bin/activate

# 3. Verify activation
echo $VIRTUAL_ENV
# Should show: /path/to/cyber-matrix/venv

# 4. Set API key (if not persistent)
export CYBER_MATRIX_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 5. Start application
python3 app.py

# 6. Access dashboard
# Open browser to: http://127.0.0.1:5000
```

### **Using the Fixed Startup Script (Easiest)**
```bash
# Just run this - it handles everything automatically
./start_fixed.sh
```

---

## 🔧 **ADVANCED TROUBLESHOOTING**

### **Database Issues**
```bash
# Reset database if corrupted
rm -f cyber_matrix.db

# Restart application (database will be recreated)
python3 app.py
```

### **Port Conflicts**
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill conflicting processes
sudo pkill -f "python.*app.py"

# Use different port
export CYBER_MATRIX_PORT=5001
python3 app.py
```

### **Permission Issues**
```bash
# Fix file permissions
chmod +x *.sh
chmod 644 *.py *.md *.txt *.html

# Run with sudo if needed (for network scanning)
sudo ./start_fixed.sh
```

### **Import Path Issues**
```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)"

# OR set it in the script
python3 -c "
import sys
sys.path.insert(0, '.')
from app import app
print('✅ Import successful')
"
```

---

## 📞 **GETTING HELP**

### **Log Files to Check**
```bash
# Application logs
tail -f cyber_matrix.log

# System logs (if using systemd)
sudo journalctl -u cyber-matrix -f

# Installation logs
cat /tmp/cyber-matrix-install.log
```

### **Common Error Messages & Solutions**

| Error | Cause | Solution |
|-------|-------|----------|
| `NameError: name 'app' is not defined` | Import order issue | Use `./start_fixed.sh` |
| `No module named 'flask'` | Dependencies not installed | `pip install flask flask-cors psutil` |
| `Permission denied` | Insufficient privileges | Run with `sudo` |
| `Port already in use` | Another service using port 5000 | Kill process or use different port |
| `Command not found` | Missing system tools | Install with package manager |

### **Emergency Reset Procedure**
If everything is broken, start completely fresh:

```bash
# 1. Remove everything
rm -rf venv cyber_matrix.db cyber_matrix.log .env

# 2. Start fresh installation
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip>=25.2
pip install flask flask-cors psutil werkzeug

# 3. Generate new API key
export CYBER_MATRIX_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 4. Start application
python3 app.py
```

---

## 🎯 **SUCCESS INDICATORS**

### **Installation Successful When:**
- ✅ Virtual environment activates without errors
- ✅ All imports work: `python3 -c "import flask, flask_cors, psutil"`
- ✅ App starts without errors: `python3 app.py`
- ✅ Web interface loads: http://127.0.0.1:5000
- ✅ Dashboard shows real system metrics

### **Application Running Properly When:**
- ✅ No error messages in console
- ✅ System metrics update in real-time
- ✅ Network scans discover actual devices
- ✅ Port scans return real results
- ✅ Console shows live system status

---

## 💡 **PRO TIPS**

### **Always Remember:**
1. **Activate virtual environment FIRST**: `source venv/bin/activate`
2. **Check your current directory**: Should be in the CYBER-MATRIX folder
3. **Use the fixed startup script**: `./start_fixed.sh` handles everything
4. **Keep your API key safe**: Note it down when generated
5. **Check logs if issues occur**: `tail -f cyber_matrix.log`

### **For Best Results:**
- Use a dedicated terminal for CYBER-MATRIX
- Keep the virtual environment activated during use
- Monitor system resources during intensive scans
- Use appropriate scan intensities for your network size

---

## 🎉 **FINAL VERIFICATION**

After following this guide, you should be able to:
- ✅ Start CYBER-MATRIX without errors
- ✅ Access the holographic dashboard
- ✅ Perform network discovery
- ✅ Execute port scans
- ✅ Run vulnerability assessments
- ✅ Use attack simulations (educational)

**If you're still having issues**, try the emergency reset procedure above or use the fixed startup script: `./start_fixed.sh`

---

**🏴‍☠️ Happy Ethical Hacking! 🏴‍☠️**