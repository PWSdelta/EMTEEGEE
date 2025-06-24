#!/usr/bin/env python3
"""
Comprehensive test of the random assignment system to ensure no duplicate work
"""

import os
import sys
import django
from collections import defaultdict

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_large_scale_assignment():
    """Test random assignments at scale to verify no duplicates"""
    
    print("🧪 Large Scale Random Assignment Test")
    print("=" * 50)
    
    num_workers = 10
    assignments = {}
    card_counts = defaultdict(int)
    
    print(f"🔄 Testing {num_workers} workers requesting work...")
    
    for i in range(num_workers):
        worker_id = f'scale_test_worker_{i+1}'
        
        # Register worker
        enhanced_swarm.register_worker(worker_id, {'type': 'test'})
        
        # Get work
        tasks = enhanced_swarm.get_work(worker_id)
        
        if tasks:
            task = tasks[0]
            card_name = task.get('card_name', 'Unknown')
            card_id = task.get('card_id', 'Unknown')
            
            assignments[worker_id] = {
                'card_name': card_name,
                'card_id': card_id
            }
            
            card_counts[card_id] += 1
            
            print(f"  👷 {worker_id}: {card_name}")
        else:
            print(f"  ❌ No work for {worker_id}")
    
    # Analysis
    print(f"\n📊 ANALYSIS:")
    print(f"  • Total workers: {num_workers}")
    print(f"  • Successful assignments: {len(assignments)}")
    print(f"  • Unique cards assigned: {len(card_counts)}")
    
    # Check for duplicates
    duplicates = {card_id: count for card_id, count in card_counts.items() if count > 1}
    
    if duplicates:
        print(f"  ⚠️  DUPLICATES FOUND:")
        for card_id, count in duplicates.items():
            card_name = next(
                (assignment['card_name'] for assignment in assignments.values() 
                 if assignment['card_id'] == card_id), 
                'Unknown'
            )
            print(f"    - {card_name}: assigned {count} times")
        return False
    else:
        print(f"  ✅ SUCCESS: No duplicate assignments!")
        return True

def test_assignment_persistence():
    """Test that assigned cards are marked as assigned to prevent reassignment"""
    
    print("\n🧪 Assignment Persistence Test")
    print("=" * 50)
    
    # Get initial assignment
    worker1_id = 'persistence_test_worker_1'
    enhanced_swarm.register_worker(worker1_id, {'type': 'test'})
    
    tasks1 = enhanced_swarm.get_work(worker1_id)
    
    if not tasks1:
        print("❌ No work available for first worker")
        return False
    
    card1_name = tasks1[0].get('card_name', 'Unknown')
    card1_id = tasks1[0].get('card_id', 'Unknown')
    
    print(f"👷 Worker 1 assigned: {card1_name}")
    
    # Try to get work for another worker - should get a different card
    worker2_id = 'persistence_test_worker_2'
    enhanced_swarm.register_worker(worker2_id, {'type': 'test'})
    
    tasks2 = enhanced_swarm.get_work(worker2_id)
    
    if not tasks2:
        print("❌ No work available for second worker")
        return False
    
    card2_name = tasks2[0].get('card_name', 'Unknown')
    card2_id = tasks2[0].get('card_id', 'Unknown')
    
    print(f"👷 Worker 2 assigned: {card2_name}")
    
    # Check if different cards
    if card1_id == card2_id:
        print(f"❌ FAILURE: Both workers assigned same card ({card1_name})")
        return False
    else:
        print(f"✅ SUCCESS: Workers assigned different cards")
        return True

if __name__ == "__main__":
    try:
        print("🚀 Comprehensive Random Assignment Tests")
        print("=" * 60)
        
        # Test 1: Large scale
        scale_test_passed = test_large_scale_assignment()
        
        # Test 2: Persistence
        persistence_test_passed = test_assignment_persistence()
        
        # Final results
        print("\n" + "=" * 60)
        print("🏁 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"Large Scale Test: {'✅ PASSED' if scale_test_passed else '❌ FAILED'}")
        print(f"Persistence Test: {'✅ PASSED' if persistence_test_passed else '❌ FAILED'}")
        
        if scale_test_passed and persistence_test_passed:
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
        else:
            print("\n⚠️  SOME TESTS FAILED. Please check the implementation.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
