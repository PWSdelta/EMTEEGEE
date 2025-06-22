#!/usr/bin/env python3
"""
Quick test of worker registration and work assignment
"""

import sys
import os

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')

import django
django.setup()

from swarm_manager_clean import SwarmManager

def test_quick():
    print("🧪 Quick Swarm Test")
    print("="*40)
    
    manager = SwarmManager()
    
    # Test desktop worker registration
    print("\n1️⃣ Testing Desktop Worker Registration...")
    desktop_result = manager.register_worker('test-desktop', {
        'gpu_available': True,
        'ram_gb': 64,
        'worker_type': 'desktop'
    })
    print(f"✅ Desktop registered: {len(desktop_result['assigned_components'])} components")
    print(f"   Components: {desktop_result['assigned_components'][:3]}...")
    
    # Test laptop worker registration
    print("\n2️⃣ Testing Laptop Worker Registration...")
    laptop_result = manager.register_worker('test-laptop', {
        'gpu_available': False,
        'ram_gb': 128,
        'worker_type': 'laptop'
    })
    print(f"✅ Laptop registered: {len(laptop_result['assigned_components'])} components")
    print(f"   Components: {laptop_result['assigned_components'][:3]}...")
    
    # Test work assignment
    print("\n3️⃣ Testing Work Assignment...")
    desktop_tasks = manager.get_work('test-desktop', max_tasks=2)
    print(f"✅ Desktop got {len(desktop_tasks)} tasks")
    
    if desktop_tasks:
        task = desktop_tasks[0]
        print(f"   Task: {task['card_name']} - {task['components']}")
    
    laptop_tasks = manager.get_work('test-laptop', max_tasks=1)
    print(f"✅ Laptop got {len(laptop_tasks)} tasks")
    
    if laptop_tasks:
        task = laptop_tasks[0]
        print(f"   Task: {task['card_name']} - {task['components']}")
    
    # Check status
    print("\n4️⃣ System Status:")
    status = manager.get_swarm_status()
    print(f"   Workers: {status['workers']['active']} active")
    print(f"   Tasks: {status['tasks']['pending']} pending")
    print(f"   Cards: {status['cards']['analyzed']:,} / {status['cards']['total']:,} analyzed")
    
    # Cleanup
    print("\n🧹 Cleanup...")
    manager.workers.delete_many({'worker_id': {'$in': ['test-desktop', 'test-laptop']}})
    manager.tasks.delete_many({'assigned_to': {'$in': ['test-desktop', 'test-laptop']}})
    print("✅ Test data cleaned up")
    
    print("\n🎉 Basic framework is working! Ready for model integration.")

if __name__ == "__main__":
    test_quick()
