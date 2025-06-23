#!/usr/bin/env python3
"""
Quick test to check if enhanced_swarm has get_work method
"""

import os
import sys
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

try:
    from cards.enhanced_swarm_manager import enhanced_swarm
    
    print(f"Enhanced swarm type: {type(enhanced_swarm)}")
    print(f"Has get_work method: {hasattr(enhanced_swarm, 'get_work')}")
    
    if hasattr(enhanced_swarm, 'get_work'):
        print("✅ get_work method exists")
        # Test calling it with safe parameters
        try:
            result = enhanced_swarm.get_work("test-worker", 1)
            print(f"✅ get_work returned: {type(result)} with {len(result)} items")
        except Exception as e:
            print(f"❌ get_work failed: {e}")
    else:
        print("❌ get_work method missing")
        print("Available methods:")
        for attr in dir(enhanced_swarm):
            if not attr.startswith('_'):
                print(f"  - {attr}")
                
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
