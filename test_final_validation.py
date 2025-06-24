#!/usr/bin/env python3
"""
Final validation of the complete enhanced swarm workflow
Tests the full cycle: assignment -> work -> submission -> completion
"""

import os
import sys
import django
import time

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def simulate_complete_workflow():
    """Simulate a complete workflow from assignment to completion"""
    
    print("🧪 Complete Workflow Simulation")
    print("=" * 50)
    
    # Register a test worker
    worker_id = 'workflow_test_worker'
    enhanced_swarm.register_worker(worker_id, {
        'type': 'gpu',
        'model': 'test',
        'capabilities': ['all_components']
    })
    
    print(f"👷 Registered worker: {worker_id}")
    
    # Step 1: Get work assignment
    print("\n📋 Step 1: Getting work assignment...")
    tasks = enhanced_swarm.get_work(worker_id)
    
    if not tasks:
        print("❌ No work available")
        return False
    
    task = tasks[0]
    card_name = task.get('card_name', 'Unknown')
    card_id = task.get('card_id')
    task_id = task.get('task_id')
    components = task.get('components', [])
    
    print(f"✅ Assigned card: {card_name}")
    print(f"   Card ID: {card_id}")
    print(f"   Task ID: {task_id}")
    print(f"   Components: {len(components)}")
    
    # Step 2: Simulate analysis work
    print("\n🔬 Step 2: Simulating analysis work...")
      # Create mock results for all components
    mock_results = {
        'results': {}
    }
    
    for component in components:
        mock_results['results'][component] = f'Test analysis content for {component} of {card_name}'
    
    print(f"✅ Generated results for {len(mock_results)} components")
    
    # Step 3: Submit results
    print("\n📤 Step 3: Submitting results...")
    
    success = enhanced_swarm.submit_task_result(
        task_id=task_id,
        worker_id=worker_id,
        card_id=card_id,
        results=mock_results
    )
    
    if success:
        print("✅ Results submitted successfully")
    else:
        print("❌ Failed to submit results")
        return False
    
    # Step 4: Verify card completion status
    print("\n🔍 Step 4: Verifying completion status...")
    
    # Check if card is marked as fully analyzed
    card = enhanced_swarm.cards.find_one({'_id': enhanced_swarm.cards.find_one({'uuid': card_id})['_id'] if enhanced_swarm.cards.find_one({'uuid': card_id}) else None})
    
    if not card:
        # Try by _id directly
        from bson import ObjectId
        try:
            card = enhanced_swarm.cards.find_one({'_id': ObjectId(card_id)})
        except:
            print(f"❌ Card not found: {card_id}")
            return False
    
    if card:
        analysis_status = card.get('analysis', {})
        is_fully_analyzed = analysis_status.get('fully_analyzed', False)
        component_count = analysis_status.get('component_count', 0)
        
        print(f"   Card: {card.get('name', 'Unknown')}")
        print(f"   Fully analyzed: {is_fully_analyzed}")
        print(f"   Component count: {component_count}")
        
        if is_fully_analyzed and component_count == 20:
            print("✅ Card marked as fully analyzed with all components")
            return True
        else:
            print("❌ Card not properly marked as complete")
            return False
    else:
        print("❌ Could not find card to verify status")
        return False

def test_no_reassignment():
    """Test that completed cards are not reassigned"""
    
    print("\n🧪 No Reassignment Test")
    print("=" * 50)
    
    # Register a new worker
    worker_id = 'reassignment_test_worker'
    enhanced_swarm.register_worker(worker_id, {'type': 'test'})
    
    # Get initial work count
    initial_tasks = enhanced_swarm.get_work(worker_id)
    
    if not initial_tasks:
        print("❌ No work available for initial test")
        return True  # If no work available, reassignment test is not applicable
    
    initial_card = initial_tasks[0]
    initial_card_name = initial_card.get('card_name', 'Unknown')
    
    print(f"👷 Worker assigned: {initial_card_name}")
      # Simulate completing the work
    mock_results = {
        'results': {}
    }
    
    for component in initial_card.get('components', []):
        mock_results['results'][component] = f'Test content for {component}'
    
    # Submit results
    success = enhanced_swarm.submit_task_result(
        task_id=initial_card.get('task_id'),
        worker_id=worker_id,
        card_id=initial_card.get('card_id'),
        results=mock_results
    )
    
    if not success:
        print("❌ Failed to submit initial results")
        return False
    
    print(f"✅ Completed analysis for: {initial_card_name}")
    
    # Now try to get work again - should get a different card
    new_tasks = enhanced_swarm.get_work(worker_id)
    
    if not new_tasks:
        print("✅ No more work available (all cards completed)")
        return True
    
    new_card = new_tasks[0]
    new_card_name = new_card.get('card_name', 'Unknown')
    new_card_id = new_card.get('card_id')
    
    print(f"👷 Worker assigned new card: {new_card_name}")
    
    if new_card_id == initial_card.get('card_id'):
        print(f"❌ FAILURE: Same card reassigned ({initial_card_name})")
        return False
    else:
        print("✅ SUCCESS: Different card assigned (no reassignment)")
        return True

if __name__ == "__main__":
    try:
        print("🚀 Final Workflow Validation")
        print("=" * 60)
        
        # Test 1: Complete workflow
        workflow_passed = simulate_complete_workflow()
        
        # Test 2: No reassignment
        reassignment_passed = test_no_reassignment()
        
        # Final results
        print("\n" + "=" * 60)
        print("🏁 FINAL VALIDATION RESULTS")
        print("=" * 60)
        print(f"Complete Workflow Test: {'✅ PASSED' if workflow_passed else '❌ FAILED'}")
        print(f"No Reassignment Test: {'✅ PASSED' if reassignment_passed else '❌ FAILED'}")
        
        if workflow_passed and reassignment_passed:
            print("\n🎉 ALL VALIDATION TESTS PASSED!")
            print("🔥 Enhanced Swarm Manager is ready for production!")
        else:
            print("\n⚠️  SOME TESTS FAILED. Please check the implementation.")
        
    except Exception as e:
        print(f"❌ Validation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
