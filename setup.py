#!/usr/bin/env python3
"""
Setup script for WhatsApp Analyzer

This script automates the installation and setup process for the WhatsApp Analyzer
with MCP client infrastructure.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_git():
    """Check if Git is installed"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git detected: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Git not found")
    print("   Please install Git from https://git-scm.com/")
    return False


def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """Get path to Python executable in virtual environment"""
    system = platform.system()
    if system == "Windows":
        return Path("venv") / "Scripts" / "python.exe"
    else:
        return Path("venv") / "bin" / "python"


def get_venv_pip():
    """Get path to pip executable in virtual environment"""
    system = platform.system()
    if system == "Windows":
        return Path("venv") / "Scripts" / "pip.exe"
    else:
        return Path("venv") / "bin" / "pip"


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    pip_path = get_venv_pip()
    
    # Upgrade pip first
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to upgrade pip: {e}")
    
    # Install requirements
    try:
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_sample_config():
    """Create sample configuration file"""
    print("⚙️  Creating sample configuration...")
    
    python_path = get_venv_python()
    
    try:
        subprocess.run([str(python_path), "mcp_config.py"], check=True)
        print("✅ Sample configuration created")
        
        # Check if mcp_config.json already exists
        if not Path("mcp_config.json").exists():
            # Copy sample to actual config
            import shutil
            shutil.copy("mcp_config_sample.json", "mcp_config.json")
            print("✅ Configuration file created: mcp_config.json")
        else:
            print("✅ Configuration file already exists: mcp_config.json")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create configuration: {e}")
        return False


def run_tests():
    """Run test suite to verify installation"""
    print("🧪 Running tests...")
    
    python_path = get_venv_python()
    
    try:
        result = subprocess.run([str(python_path), "test_mcp_client.py"], 
                              capture_output=True, text=True, check=True)
        print("✅ All tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def print_activation_instructions():
    """Print instructions for activating virtual environment"""
    system = platform.system()
    
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    
    if system == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Configure your MCP server endpoint in mcp_config.json")
    print("\n3. Start your WhatsApp MCP server")
    print("\n4. Run the analyzer:")
    print("   python extract_whatsapp_data.py")
    
    print("\n📚 Documentation:")
    print("   - README.md - Main documentation")
    print("   - INSTALLATION.md - Detailed installation guide")
    print("   - MCP_CLIENT_DOCUMENTATION.md - MCP client API reference")
    
    print("\n🧪 Test your setup:")
    print("   python test_mcp_client.py")


def print_error_help():
    """Print help information for common errors"""
    print("\n" + "="*60)
    print("❌ Installation failed")
    print("="*60)
    
    print("\n🔧 Troubleshooting:")
    print("1. Ensure Python 3.8+ is installed")
    print("2. Check internet connectivity for downloading packages")
    print("3. Try running with administrator/sudo privileges")
    print("4. Check antivirus software isn't blocking the installation")
    
    print("\n📖 For detailed help, see:")
    print("   - INSTALLATION.md")
    print("   - https://github.com/Schulman-Coaching/WhatsApp-Analyzer")


def main():
    """Main setup function"""
    print("🚀 WhatsApp Analyzer Setup")
    print("="*40)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    # Git check is optional for local setup
    check_git()
    
    # Create virtual environment
    if not create_virtual_environment():
        print_error_help()
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print_error_help()
        return 1
    
    # Create configuration
    if not create_sample_config():
        print_error_help()
        return 1
    
    # Run tests
    if not run_tests():
        print("⚠️  Tests failed, but installation may still work")
        print("   Try running manually: python test_mcp_client.py")
    
    # Print success message
    print_activation_instructions()
    return 0


if __name__ == "__main__":
    sys.exit(main())