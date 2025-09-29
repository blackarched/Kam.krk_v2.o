# 🚀 CYBER-MATRIX v8.0 - Secure Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for securely deploying the enhanced CYBER-MATRIX v8.0 penetration testing tool. The tool has been completely overhauled with security improvements and is now ready for educational and authorized testing environments.

## ⚡ Quick Start (Recommended)

### **Method 1: Automated Secure Setup**
```bash
# 1. Clone or download the enhanced version
cd /workspace

# 2. Set up environment variables
export CYBER_MATRIX_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "API Key: $CYBER_MATRIX_API_KEY"

# 3. Make startup script executable
chmod +x start.sh

# 4. Run the secure application
sudo ./start.sh
```

### **Method 2: Manual Setup**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install secure dependencies
pip install -r requirements.txt

# 3. Initialize secure database
python3 -c "
import sqlite3
conn = sqlite3.connect('cyber_matrix.db')
# Database tables are auto-created by app.py
conn.close()
"

# 4. Set environment variables
export CYBER_MATRIX_API_KEY="your-secure-api-key-here"

# 5. Run the application
python3 app.py
```

## 🔒 Security Configuration

### **API Key Setup**
```bash
# Generate a secure API key
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Set environment variable
export CYBER_MATRIX_API_KEY="$API_KEY"

# For persistent setup, add to ~/.bashrc or create .env file
echo "export CYBER_MATRIX_API_KEY='$API_KEY'" >> ~/.bashrc
```

### **Using the API Key**
```bash
# Method 1: Header-based authentication
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/system/metrics

# Method 2: Query parameter authentication
curl "http://localhost:5000/api/system/metrics?api_key=your-api-key"
```

## 🌐 Access Information

Once deployed, access the application at:
- **Local Access**: http://localhost:5000
- **Network Access**: http://your-ip:5000
- **API Documentation**: Available in the web interface

### **Default Credentials**
- **API Key**: Generated during setup (see console output)
- **Web Interface**: No additional login required (protected by API key)

## 🛡️ Security Features Enabled

### **Input Validation**
- ✅ IP address format validation
- ✅ Port range validation (single, ranges, comma-separated)
- ✅ CIDR notation validation
- ✅ Input sanitization for all user inputs

### **Command Injection Prevention**
- ✅ No `shell=True` usage in subprocess calls
- ✅ Command whitelist enforcement
- ✅ Path validation for executables
- ✅ Argument sanitization

### **API Security**
- ✅ API key authentication required
- ✅ Rate limiting per endpoint
- ✅ Request validation and sanitization
- ✅ Secure error handling

### **Database Security**
- ✅ Parameterized queries only
- ✅ No SQL injection vulnerabilities
- ✅ Input validation before database operations

## 📊 Available Features

### **Network Discovery**
```bash
# Secure network scanning
curl -H "X-API-Key: $API_KEY" -X POST \
  -H "Content-Type: application/json" \
  -d '{"ip_range":"192.168.1.0/24"}' \
  http://localhost:5000/api/network/scan
```

### **Port Scanning**
```bash
# Secure port scanning
curl -H "X-API-Key: $API_KEY" -X POST \
  -H "Content-Type: application/json" \
  -d '{"target_ip":"192.168.1.1","port_range":"22,80,443"}' \
  http://localhost:5000/api/port/scan
```

### **Vulnerability Assessment**
```bash
# Secure vulnerability scanning
curl -H "X-API-Key: $API_KEY" -X POST \
  -H "Content-Type: application/json" \
  -d '{"target_ip":"192.168.1.1","intensity":"medium"}' \
  http://localhost:5000/api/vulnerability/scan
```

### **Educational Simulations**
```bash
# Security test simulation (educational only)
curl -H "X-API-Key: $API_KEY" -X POST \
  -H "Content-Type: application/json" \
  -d '{"target_ip":"192.168.1.1","protocol":"ssh"}' \
  http://localhost:5000/api/attack/hydra
```

## 🔧 Configuration Options

### **Rate Limiting**
Adjust rate limits in `app.py`:
```python
# Network scans: 10 requests per minute
@rate_limit(max_requests=10, window=60)

# Port scans: 5 requests per minute  
@rate_limit(max_requests=5, window=60)

# Vulnerability scans: 3 requests per 5 minutes
@rate_limit(max_requests=3, window=300)
```

### **Logging Configuration**
```python
# Enable debug logging
export FLASK_DEBUG=1

# Set log level
logging.basicConfig(level=logging.INFO)
```

### **Database Configuration**
```python
# Default SQLite database
DB_FILE = 'cyber_matrix.db'

# Tables auto-created:
# - scan_results
# - network_devices  
# - attack_logs
# - system_metrics
```

## 🚨 Security Warnings & Best Practices

### **⚠️ Legal & Ethical Usage**
- **ONLY** use on networks you own or have explicit written permission to test
- This tool is for **EDUCATIONAL** and **AUTHORIZED TESTING** purposes only
- Unauthorized network scanning and attacks are **ILLEGAL**
- Always follow **responsible disclosure** practices

### **🔒 Production Security**
For production deployment, ensure:

1. **HTTPS/TLS Encryption**
```bash
# Use a reverse proxy like nginx with SSL
# Configure proper TLS certificates
# Redirect HTTP to HTTPS
```

2. **Firewall Configuration**
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 443   # HTTPS
sudo ufw deny 5000   # Block direct access to app
sudo ufw enable
```

3. **Network Segmentation**
```bash
# Deploy in isolated network segment
# Use VPN for remote access
# Implement network access controls
```

4. **Monitoring & Alerting**
```bash
# Set up log monitoring
# Configure security alerts
# Implement intrusion detection
```

## 🐛 Troubleshooting

### **Common Issues**

**API Key Authentication Fails**
```bash
# Check environment variable
echo $CYBER_MATRIX_API_KEY

# Verify API key in request
curl -v -H "X-API-Key: $API_KEY" http://localhost:5000/api/system/metrics
```

**Rate Limit Exceeded**
```bash
# Wait for rate limit window to reset
# Check rate limit settings in app.py
# Consider increasing limits for your use case
```

**Command Not Found Errors**
```bash
# Install missing network tools
sudo apt update
sudo apt install nmap hydra nikto

# Check tool availability
which nmap
which hydra
```

**Permission Denied**
```bash
# Run with appropriate privileges
sudo ./start.sh

# Check file permissions
chmod +x start.sh
chmod +r requirements.txt
```

**Port Already in Use**
```bash
# Kill existing processes
sudo lsof -ti:5000 | xargs kill -9

# Use different port
export FLASK_PORT=5001
python3 app.py
```

## 📈 Performance Optimization

### **System Requirements**
- **Minimum**: 2GB RAM, 1GB disk space
- **Recommended**: 4GB RAM, 2GB disk space
- **Network**: 100Mbps for optimal performance

### **Performance Tuning**
```python
# Adjust concurrent scan limits
system_metrics['active_scans'] >= 3  # Max concurrent

# Database optimization
# SQLite is sufficient for most use cases
# Consider PostgreSQL for high-volume deployments

# Memory optimization
# Monitor with: ps aux | grep python
# Use memory profiling tools if needed
```

## 🔄 Updates & Maintenance

### **Security Updates**
```bash
# Regular dependency updates
pip install --upgrade -r requirements.txt

# Check for security advisories
pip audit

# Update system packages
sudo apt update && sudo apt upgrade
```

### **Backup & Recovery**
```bash
# Backup database
cp cyber_matrix.db cyber_matrix.db.backup

# Backup configuration
tar -czf cyber-matrix-backup.tar.gz .env *.py *.md

# Restore from backup
tar -xzf cyber-matrix-backup.tar.gz
```

## 📞 Support & Resources

### **Documentation**
- `README.md` - General information and features
- `SECURITY_REPORT.md` - Detailed security analysis
- `INTEGRATION_SCORESHEET.md` - Integration assessment

### **Logs & Debugging**
```bash
# View application logs
tail -f cyber_matrix.log

# Enable debug mode
export FLASK_DEBUG=1
python3 app.py

# Check system resources
htop
df -h
```

### **Community & Support**
- Review security best practices regularly
- Keep dependencies updated
- Monitor for new vulnerabilities
- Follow cybersecurity news and updates

---

## ✅ Deployment Checklist

Before going live, ensure:

- [ ] API key generated and configured
- [ ] All dependencies installed and updated
- [ ] Security tests passed
- [ ] Rate limits configured appropriately
- [ ] Logging enabled and monitored
- [ ] Network security configured
- [ ] Legal authorization obtained
- [ ] Backup procedures established
- [ ] Monitoring and alerting configured
- [ ] Documentation reviewed and understood

---

**🎉 Congratulations!** Your CYBER-MATRIX v8.0 deployment is now secure and ready for educational cybersecurity training and authorized testing activities.

**Remember**: With great power comes great responsibility. Use this tool ethically and legally!