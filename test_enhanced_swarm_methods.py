#!/usr/bin/env python3
"""
Quick test to verify EnhancedSwarmManager methods
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def test_enhanced_swarm_manager():
    """Test if the EnhancedSwarmManager has the required methods"""
    print("🔍 Testing Enhanced Swarm Manager...")
    
    try:
        # Import the manager
        from cards.enhanced_swarm_manager import enhanced_swarm
        
        print(f"✅ Enhanced Swarm Manager imported successfully")
        print(f"📋 Type: {type(enhanced_swarm)}")
        
        # Check if methods exist
        methods_to_check = [
            'get_work',
            'submit_task_result', 
            'submit_enhanced_results',
            'register_worker',
            'get_enhanced_swarm_status'
        ]
        
        for method_name in methods_to_check:
            if hasattr(enhanced_swarm, method_name):
                method = getattr(enhanced_swarm, method_name)
                print(f"✅ Method {method_name}: {type(method)}")
            else:
                print(f"❌ Method {method_name}: NOT FOUND")
        
        # List all methods
        print("\n📝 All methods:")
        all_methods = [method for method in dir(enhanced_swarm) if not method.startswith('_')]
        for method in sorted(all_methods):
            print(f"  - {method}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_swarm_manager()
