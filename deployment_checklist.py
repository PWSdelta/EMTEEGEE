#!/usr/bin/env python3
"""
Simple Swarm API Deployment Checklist
Quick verification of required files for production deployment
"""

import os

def check_deployment_files():
    """Check if all required swarm files exist locally"""
    
    required_files = [
        'cards/swarm_api.py',
        'cards/api_urls.py', 
        'swarm_manager_simple.py',
        'emteegee/urls.py'
    ]
    
    print("🔍 Checking required swarm files for deployment...")
    print("=" * 50)
    
    all_files_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_files_exist = False
    
    print("\n📋 URL Configuration Check:")
    print("-" * 30)
    
    # Check if main urls.py includes swarm routes
    try:
        with open('emteegee/urls.py', 'r') as f:
            urls_content = f.read()
            if 'api/swarm/' in urls_content and 'cards.api_urls' in urls_content:
                print("✅ emteegee/urls.py includes swarm routes")
            else:
                print("❌ emteegee/urls.py missing swarm route configuration")
                print("   Add this line: path('api/swarm/', include('cards.api_urls')),")
                all_files_exist = False
    except FileNotFoundError:
        print("❌ emteegee/urls.py not found")
        all_files_exist = False
    
    print(f"\n🎯 Deployment Status:")
    if all_files_exist:
        print("✅ All required files present - READY FOR DEPLOYMENT")
        print("\n📤 Next Steps:")
        print("1. Upload these files to your production server")
        print("2. Restart Django service")
        print("3. Test: http://64.23.130.187:8000/api/swarm/status")
        print("4. Run distributed workers")
    else:
        print("❌ Missing required files - FIX BEFORE DEPLOYMENT")
    
    return all_files_exist

if __name__ == "__main__":
    check_deployment_files()
