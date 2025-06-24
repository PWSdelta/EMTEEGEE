#!/usr/bin/env python3
"""
Debug the actual submission format being sent by workers
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm
import json

def debug_actual_submission():
    print("🔍 DEBUGGING ACTUAL WORKER SUBMISSIONS")
    print("=" * 50)
    
    # Look at the most recent completed task to see what was actually submitted
    recent_completed = list(enhanced_swarm.tasks.find({
        'status': 'completed'
    }).sort('completed_at', -1).limit(5))
    
    print(f"📊 Found {len(recent_completed)} recent completed tasks")
    
    for i, task in enumerate(recent_completed, 1):
        print(f"\n{i}. Task: {task.get('task_id', 'unknown')}")
        print(f"   Card: {task.get('card_name', 'unknown')}")
        print(f"   Worker: {task.get('assigned_to', 'unknown')}")
        print(f"   Completed: {task.get('completed_at', 'unknown')}")
        
        # Check if there are results stored in the task
        if 'results' in task:
            print(f"   ✅ Task has results field")
            results = task['results']
            print(f"   Results type: {type(results)}")
            if isinstance(results, dict):
                print(f"   Results keys: {list(results.keys())}")
                for key, value in results.items():
                    print(f"     {key}: {str(value)[:100]}...")
        else:
            print("   ❌ Task has no results field")
    
    # Also check what's in the actual card analysis
    print("\n" + "=" * 50)
    print("📋 CHECKING ACTUAL CARD ANALYSIS DATA")
    
    for task in recent_completed[:3]:
        card_name = task.get('card_name', 'unknown')
        card_id = task.get('card_id')
        
        if card_id:
            from bson import ObjectId
            try:
                card = enhanced_swarm.cards.find_one({'_id': ObjectId(card_id)})
                if card:
                    print(f"\n📋 Card: {card_name}")
                    analysis = card.get('analysis', {})
                    components = analysis.get('components', {})
                    print(f"   Component count: {analysis.get('component_count', 0)}")
                    print(f"   Components keys: {list(components.keys())}")
                    print(f"   Fully analyzed: {analysis.get('fully_analyzed', False)}")
                    
                    # Show first component content
                    if components:
                        first_component = list(components.items())[0]
                        comp_name, comp_data = first_component
                        if isinstance(comp_data, dict):
                            content = comp_data.get('content', 'no content')
                            print(f"   Sample content ({comp_name}): {content[:200]}...")
                        else:
                            print(f"   Sample content ({comp_name}): {str(comp_data)[:200]}...")
                else:
                    print(f"\n❌ Card not found for {card_name}")
            except Exception as e:
                print(f"\n❌ Error checking card {card_name}: {e}")

if __name__ == "__main__":
    debug_actual_submission()