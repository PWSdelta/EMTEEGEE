#!/usr/bin/env python3
"""
Quick test to check if get_work method exists
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from cards.enhanced_swarm_manager import EnhancedSwarmManager
    
    # Create a fresh instance
    manager = EnhancedSwarmManager()
    
    print("✅ EnhancedSwarmManager imported successfully")
    print(f"Methods: {[method for method in dir(manager) if not method.startswith('_')]}")
    print(f"Has get_work: {hasattr(manager, 'get_work')}")
    
    if hasattr(manager, 'get_work'):
        print("🎉 get_work method found!")
    else:
        print("❌ get_work method missing")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
