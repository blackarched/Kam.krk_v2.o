#!/usr/bin/env python3
"""
CYBER-MATRIX v8.0 - Quick Fix Script
Fixes import issues and ensures proper setup
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing required dependencies...")
    
    # Core dependencies that are absolutely required
    core_deps = [
        "flask>=3.0.0",
        "flask-cors>=4.0.0", 
        "psutil>=5.9.0",
        "werkzeug>=3.0.0"
    ]
    
    for dep in core_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def test_imports():
    """Test if critical imports work"""
    print("\n🧪 Testing critical imports...")
    
    try:
        import flask
        print("✅ Flask import successful")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_cors
        print("✅ Flask-CORS import successful")
    except ImportError as e:
        print(f"❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil import successful")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    return True

def main():
    print("🚀 CYBER-MATRIX v8.0 - Quick Fix Script")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment. Consider using: source venv/bin/activate")
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Import testing failed")
        return False
    
    print("\n✅ All fixes applied successfully!")
    print("\n🚀 You can now run: python3 app.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)