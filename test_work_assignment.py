#!/usr/bin/env python3
"""
Test Worker Assignment - Debug why workers aren't getting tasks
"""

import os
import django
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_worker_assignment():
    """Test what happens when a worker requests work"""
    print("🔍 TESTING WORKER ASSIGNMENT")
    print("=" * 50)
    
    # Simulate a worker requesting work
    test_worker_id = "test_worker_debug"
    
    try:
        print(f"� Requesting work for worker: {test_worker_id}")
        
        # Call the same method the API calls
        tasks = enhanced_swarm.get_work(test_worker_id)
        
        print(f"📊 Number of tasks returned: {len(tasks)}")
        
        if tasks:
            for i, task in enumerate(tasks, 1):
                print(f"✅ Task {i}:")
                print(f"   - Task ID: {task.get('task_id', 'N/A')}")
                print(f"   - Card ID: {task.get('card_id', 'N/A')}")
                print(f"   - Card Name: {task.get('card_name', 'N/A')}")
                print(f"   - Components: {len(task.get('components', []))}")
                print(f"   - Status: {task.get('status', 'N/A')}")
        else:
            print("❌ No tasks returned")
            
            # Let's debug why - check if cards exist
            print("\n🔍 DEBUGGING WHY NO TASKS...")
            
            # Test the exact same pipeline used in get_work
            pipeline = [
                {
                    '$match': {
                        '$or': [
                            {'analysis.fully_analyzed': {'$ne': True}},
                            {'analysis': {'$exists': False}},
                            {'analysis.component_count': {'$lt': 20}}
                        ]
                    }
                },
                {'$sample': {'size': 1}},
                {
                    '$project': {
                        '_id': 1,
                        'name': 1,
                        'manaCost': 1,
                        'type': 1,
                        'text': 1,
                        'power': 1,
                        'toughness': 1
                    }
                }
            ]
            
            test_cards = list(enhanced_swarm.cards.aggregate(pipeline))
            
            if test_cards:
                card = test_cards[0]
                print(f"✅ Pipeline found card: {card.get('name', 'Unknown')}")
                print(f"   - Card ID: {card['_id']}")
                print(f"   - Has required fields: {bool(card.get('name'))}")
            else:
                print("❌ Pipeline returned no cards")
                
    except Exception as e:
        print(f"❌ Error during work assignment: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_worker_assignment()