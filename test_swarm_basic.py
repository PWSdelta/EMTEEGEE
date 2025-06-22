#!/usr/bin/env python3
"""
Test script for the AI Analysis Swarm System
Tests basic functionality without running full server
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')

import django
django.setup()

from swarm_manager_clean import SwarmManager

def test_swarm_manager():
    """Test basic SwarmManager functionality"""
    print("🧪 Testing SwarmManager...")
    
    try:
        manager = SwarmManager()
        print("✅ SwarmManager initialized successfully")
        
        # Test status
        status = manager.get_swarm_status()
        print("✅ Status retrieved successfully")
        print(f"   Cards: {status['cards']['total']:,} total, {status['cards']['analyzed']:,} analyzed")
        
        return True
        
    except Exception as e:
        print(f"❌ SwarmManager test failed: {e}")
        return False

def test_worker_registration():
    """Test worker registration"""
    print("\n🧪 Testing Worker Registration...")
    
    try:
        manager = SwarmManager()
        
        # Test desktop worker registration
        desktop_capabilities = {
            'hostname': 'test-desktop',
            'gpu_available': True,
            'ram_gb': 64,
            'cpu_cores': 16,
            'worker_type': 'desktop'
        }
        
        result = manager.register_worker('test-desktop-001', desktop_capabilities)
        print("✅ Desktop worker registered successfully")
        print(f"   Assigned components: {len(result['assigned_components'])} components")
        
        # Test laptop worker registration
        laptop_capabilities = {
            'hostname': 'test-laptop',
            'gpu_available': False,
            'ram_gb': 128,
            'cpu_cores': 32,
            'worker_type': 'laptop'
        }
        
        result = manager.register_worker('test-laptop-001', laptop_capabilities)
        print("✅ Laptop worker registered successfully")
        print(f"   Assigned components: {len(result['assigned_components'])} components")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker registration test failed: {e}")
        return False

def test_work_assignment():
    """Test work assignment logic"""
    print("\n🧪 Testing Work Assignment...")
    
    try:
        manager = SwarmManager()
        
        # Get work for desktop worker
        desktop_tasks = manager.get_work('test-desktop-001', max_tasks=2)
        print(f"✅ Desktop worker got {len(desktop_tasks)} tasks")
        
        # Get work for laptop worker
        laptop_tasks = manager.get_work('test-laptop-001', max_tasks=1)
        print(f"✅ Laptop worker got {len(laptop_tasks)} tasks")
        
        if desktop_tasks:
            print(f"   Desktop task sample: {desktop_tasks[0]['card_name']} - {desktop_tasks[0]['components']}")
        
        if laptop_tasks:
            print(f"   Laptop task sample: {laptop_tasks[0]['card_name']} - {laptop_tasks[0]['components']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Work assignment test failed: {e}")
        return False

def test_component_routing():
    """Test that components are routed to correct worker types"""
    print("\n🧪 Testing Component Routing...")
    
    try:
        manager = SwarmManager()
        
        # Test desktop components
        desktop_caps = {'gpu_available': True, 'ram_gb': 64, 'cpu_cores': 16}
        desktop_components = manager._get_worker_components(desktop_caps)
        
        # Test laptop components  
        laptop_caps = {'gpu_available': False, 'ram_gb': 128, 'cpu_cores': 32}
        laptop_components = manager._get_worker_components(laptop_caps)
        
        print(f"✅ Desktop gets {len(desktop_components)} component types")
        print(f"   GPU components: {[c for c in desktop_components if c in manager.GPU_COMPONENTS]}")
        
        print(f"✅ Laptop gets {len(laptop_components)} component types")
        print(f"   CPU components: {[c for c in laptop_components if c in manager.CPU_HEAVY_COMPONENTS]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component routing test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test workers"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        manager = SwarmManager()
        
        # Remove test workers
        manager.workers.delete_many({'worker_id': {'$in': ['test-desktop-001', 'test-laptop-001']}})
        
        # Remove test tasks
        manager.tasks.delete_many({'assigned_to': {'$in': ['test-desktop-001', 'test-laptop-001']}})
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Run all tests"""
    print("🐝 AI Analysis Swarm System - Basic Framework Test")
    print("="*60)
    
    tests = [
        test_swarm_manager,
        test_worker_registration,
        test_work_assignment,
        test_component_routing
    ]
    
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    cleanup_test_data()
    
    print("\n" + "="*60)
    print(f"🎯 Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Basic framework is working.")
        print("\nNext steps:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Test API endpoints")
        print("3. Run desktop worker: python desktop_worker.py")
        print("4. Run laptop worker: python laptop_worker.py")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
