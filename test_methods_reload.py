#!/usr/bin/env python3
"""
Force reload and test Enhanced Swarm Manager
"""

import os
import sys
import importlib

# Clean up any cached modules
if 'cards.enhanced_swarm_manager' in sys.modules:
    del sys.modules['cards.enhanced_swarm_manager']

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def test_methods_after_reload():
    """Test methods after forcing module reload"""
    print("🔄 Force reloading Enhanced Swarm Manager...")
    
    try:
        # Force fresh import
        from cards import enhanced_swarm_manager
        importlib.reload(enhanced_swarm_manager)
        
        # Get fresh instance
        enhanced_swarm = enhanced_swarm_manager.enhanced_swarm
        
        print(f"✅ Fresh import completed")
        
        # Check critical methods
        methods_to_check = ['get_work', 'submit_task_result']
        
        for method_name in methods_to_check:
            if hasattr(enhanced_swarm, method_name):
                print(f"✅ Method {method_name}: FOUND")
            else:
                print(f"❌ Method {method_name}: NOT FOUND")
        
        # Try calling get_work to see if it works
        print("\n🧪 Testing get_work method:")
        result = enhanced_swarm.get_work("test-worker", 1)
        print(f"✅ get_work returned: {type(result)} with {len(result)} tasks")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_methods_after_reload()
