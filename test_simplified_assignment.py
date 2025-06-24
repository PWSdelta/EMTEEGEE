#!/usr/bin/env python3
"""
Test the simplified work assignment logic
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_simplified_assignment():
    """Test the new simplified work assignment"""
    print("🧪 TESTING SIMPLIFIED WORK ASSIGNMENT")
    print("=" * 50)
    
    # Test multiple workers to ensure no conflicts
    workers = ['test_worker_1', 'test_worker_2', 'test_worker_3']
    
    print("\n📋 Getting work assignments for 3 workers...")
    assignments = {}
    
    for worker_id in workers:
        print(f"\n🔄 Getting work for {worker_id}...")
        tasks = enhanced_swarm.get_work(worker_id)
        
        if tasks:
            task = tasks[0]
            card_name = task.get('card_name', 'Unknown')
            components = task.get('components', [])
            card_uuid = task.get('card_uuid', '')
            
            print(f"✅ {worker_id} assigned: {card_name}")
            print(f"   📦 Components: {len(components)} total")
            print(f"   🎯 UUID: {card_uuid}")
            print(f"   🧩 Component list: {components[:5]}...")
            
            assignments[worker_id] = {
                'card_name': card_name,
                'card_uuid': card_uuid,
                'component_count': len(components)
            }
        else:
            print(f"❌ {worker_id} got no work")
    
    print(f"\n📊 ASSIGNMENT SUMMARY:")
    print(f"Total assignments: {len(assignments)}")
    
    # Check for duplicate assignments
    card_uuids = [a['card_uuid'] for a in assignments.values()]
    if len(card_uuids) != len(set(card_uuids)):
        print("⚠️  WARNING: Duplicate card assignments detected!")
        for worker, assignment in assignments.items():
            print(f"   {worker}: {assignment['card_name']} ({assignment['card_uuid']})")
    else:
        print("✅ No duplicate assignments - each worker got a different card!")
    
    # Verify component counts
    for worker, assignment in assignments.items():
        count = assignment['component_count']
        if count == 20:
            print(f"✅ {worker}: Correct component count ({count})")
        else:
            print(f"❌ {worker}: Wrong component count ({count}, expected 20)")
    
    print(f"\n🎯 Next Steps:")
    print("1. Check that Sol Ring and Command Tower aren't repeatedly assigned")
    print("2. Verify workers can actually process all 20 components") 
    print("3. Test the submit_task_result method with full results")

if __name__ == "__main__":
    test_simplified_assignment()
