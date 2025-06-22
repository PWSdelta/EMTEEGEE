#!/usr/bin/env python3
"""
Setup script for AI Analysis Swarm System
Installs dependencies and sets up the system
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"   Error: {e.stderr}")
        return False

def install_python_packages():
    """Install required Python packages"""
    print("📦 Installing Python packages...")
    
    packages = [
        'requests',
        'psutil', 
        'redis',
        'celery',  # For advanced task queuing if needed
    ]
    
    for package in packages:
        success = run_command(f"pip install {package}")
        if not success:
            print(f"Failed to install {package}, continuing...")

def setup_redis():
    """Instructions for Redis setup"""
    print("\n🔴 Redis Setup Required:")
    print("   Redis is used for real-time task queuing (optional but recommended)")
    print("   ")
    print("   Windows: Download Redis from https://github.com/microsoftarchive/redis/releases")
    print("   Linux/Mac: apt install redis-server  or  brew install redis")
    print("   ")
    print("   Start Redis server before running the swarm system")

def create_systemd_services():
    """Create systemd service files for Linux"""
    if os.name != 'posix':
        return
    
    print("\n🔧 Creating systemd service files...")
    
    # This would create service files for auto-starting workers
    # Skipping implementation for now

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        'logs/swarm',
        'data/swarm_cache'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}")

def test_installation():
    """Test the swarm system installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import requests
        import psutil
        print("✅ All Python packages imported successfully")
        
        # Test swarm manager
        from swarm_manager import SwarmManager
        manager = SwarmManager()
        print("✅ SwarmManager initialized successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def main():
    """Main setup routine"""
    print("🐝 AI Analysis Swarm System Setup")
    print("="*50)
    
    # Install packages
    install_python_packages()
    
    # Setup Redis info
    setup_redis()
    
    # Create directories
    setup_directories()
    
    # Test installation
    success = test_installation()
    
    print("\n" + "="*50)
    if success:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start Redis server (if using)")
        print("2. Start Django server: python manage.py runserver")
        print("3. Run desktop worker: python desktop_worker.py")
        print("4. Run laptop worker: python laptop_worker.py")
        print("5. Monitor with: python swarm_dashboard.py --interactive")
    else:
        print("❌ Setup encountered errors")
        print("Please resolve the issues above and run setup again")

if __name__ == "__main__":
    main()
