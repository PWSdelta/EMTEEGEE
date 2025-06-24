#!/usr/bin/env python3
"""
Test script to verify random assignment logic in enhanced swarm manager
"""

import os
import sys
import django
import time
from datetime import datetime

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_random_assignment():
    """Test that multiple workers get different cards using random assignment"""
    
    print("🧪 Testing Random Assignment Logic")
    print("=" * 50)
    
    # Test multiple workers requesting work
    workers = ['test_worker_1', 'test_worker_2', 'test_worker_3']
    assignments = {}
    
    print("🔄 Requesting work for 3 different workers...")
    
    for worker_id in workers:
        print(f"\n📋 Getting work for {worker_id}...")
        
        # Register worker first
        enhanced_swarm.register_worker(worker_id, {'type': 'test'})
        
        # Get work assignment
        tasks = enhanced_swarm.get_work(worker_id)
        
        if tasks:
            task = tasks[0]
            card_name = task.get('card_name', 'Unknown')
            card_id = task.get('card_id', 'Unknown')
            component_count = len(task.get('components', []))
            
            assignments[worker_id] = {
                'card_name': card_name,
                'card_id': card_id,
                'component_count': component_count,
                'task_id': task.get('task_id')
            }
            
            print(f"  ✅ Assigned: {card_name} ({component_count} components)")
        else:
            print(f"  ❌ No work available for {worker_id}")
    
    print("\n" + "=" * 50)
    print("📊 ASSIGNMENT SUMMARY")
    print("=" * 50)
    
    # Check for duplicate assignments
    assigned_cards = []
    for worker_id, assignment in assignments.items():
        card_name = assignment['card_name']
        card_id = assignment['card_id']
        
        print(f"👷 {worker_id}: {card_name} (ID: {card_id[:8]}...)")
        
        if card_id in assigned_cards:
            print(f"  ⚠️  WARNING: Card {card_name} assigned to multiple workers!")
        else:
            assigned_cards.append(card_id)
    
    # Results
    unique_assignments = len(set(assignment['card_id'] for assignment in assignments.values()))
    total_assignments = len(assignments)
    
    print(f"\n📈 RESULTS:")
    print(f"  • Total assignments: {total_assignments}")
    print(f"  • Unique cards assigned: {unique_assignments}")
    print(f"  • Duplicate assignments: {total_assignments - unique_assignments}")
    
    if unique_assignments == total_assignments:
        print("  ✅ SUCCESS: All workers received different cards!")
    else:
        print("  ❌ FAILURE: Some workers received the same card!")
    
    return unique_assignments == total_assignments

def test_component_count():
    """Test that each assignment includes all 20 components"""
    
    print("\n🧪 Testing Component Count")
    print("=" * 50)
    
    # Register a test worker
    worker_id = 'component_test_worker'
    enhanced_swarm.register_worker(worker_id, {'type': 'test'})
    
    # Get work assignment
    tasks = enhanced_swarm.get_work(worker_id)
    
    if tasks:
        task = tasks[0]
        components = task.get('components', [])
        card_name = task.get('card_name', 'Unknown')
        
        print(f"📋 Card: {card_name}")
        print(f"🔧 Components assigned: {len(components)}")
        
        if len(components) == 20:
            print("  ✅ SUCCESS: All 20 components assigned!")
            return True
        else:
            print(f"  ❌ FAILURE: Only {len(components)} components assigned!")
            print("  Components:", components)
            return False
    else:
        print("  ❌ No work available for testing")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced Swarm Manager Tests")
        print("=" * 60)
        
        # Test 1: Random assignment
        random_test_passed = test_random_assignment()
        
        # Test 2: Component count
        component_test_passed = test_component_count()
        
        # Final results
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"Random Assignment Test: {'✅ PASSED' if random_test_passed else '❌ FAILED'}")
        print(f"Component Count Test: {'✅ PASSED' if component_test_passed else '❌ FAILED'}")
        
        if random_test_passed and component_test_passed:
            print("\n🎉 ALL TESTS PASSED! Random assignment is working correctly.")
        else:
            print("\n⚠️  SOME TESTS FAILED. Please check the implementation.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
