#!/usr/bin/env python3
"""
Setup script to install required dependencies for Scryfall import.
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Install required packages."""
    required_packages = [
        "requests",  # For HTTP requests to Scryfall API
    ]
    
    print("Installing required packages for Scryfall import...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            install_package(package)
            print(f"✅ {package} installed successfully")
    
    print("\n🎉 All dependencies installed!")
    print("\nYou can now run:")
    print("python manage.py import_scryfall_data")

if __name__ == "__main__":
    main()
