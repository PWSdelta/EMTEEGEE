#!/usr/bin/env python3
"""
Debug script to analyze result submission failures with correct field names
"""

import os
import sys
import django
from pprint import pprint
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from pymongo import MongoClient

def debug_result_submission():
    """Debug result submission failures"""
    print("🔍 Debugging result submission failures...")
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emteegee_dev']
    
    # Get recent tasks
    tasks = list(db.swarm_tasks.find().sort('_id', -1).limit(5))
    
    print(f"📋 Recent tasks: {len(tasks)}")
    for task in tasks:
        print(f"  Task: {task['task_id']}")
        print(f"  Card: {task['card_name']} (ID: {task['card_id']})")
        print(f"  Status: {task['status']}")
        print(f"  Assigned to: {task.get('assigned_to', 'None')}")
        print(f"  Components: {len(task.get('components', []))}")
        print()
    
    # Look for failed/stuck tasks
    failed_tasks = list(db.swarm_tasks.find({'status': {'$in': ['assigned', 'processing']}}))
    print(f"🚫 Tasks in progress/stuck: {len(failed_tasks)}")
    
    # Check if there are any completed tasks
    completed_tasks = list(db.swarm_tasks.find({'status': 'completed'}))
    print(f"✅ Completed tasks: {len(completed_tasks)}")
    
    # Now let's test the card lookup that happens during result submission
    print("\n🔍 Testing card lookup for result submission...")
    
    for task in tasks[:2]:  # Test first 2 tasks
        card_id = task['card_id']
        print(f"\n🎯 Testing lookup for card_id: {card_id}")
        
        # This is what the result submission does - look up by uuid first
        card_by_uuid = db.cards.find_one({'uuid': card_id})
        print(f"  Lookup by uuid: {'✅ Found' if card_by_uuid else '❌ Not found'}")
        
        # Then look up by id
        card_by_id = db.cards.find_one({'id': card_id})
        print(f"  Lookup by id: {'✅ Found' if card_by_id else '❌ Not found'}")
        
        # Check if there's a card with a different ID format
        if not card_by_uuid and not card_by_id:
            # Try to find any card with similar name
            card_by_name = db.cards.find_one({'name': task['card_name']})
            if card_by_name:
                print(f"  Card found by name with uuid: {card_by_name.get('uuid')}")
                print(f"  Card found by name with id: {card_by_name.get('id')}")
            else:
                print(f"  ❌ No card found by name either")
    
    # Test the actual result submission endpoint
    print("\n🧪 Testing result submission endpoint...")
    
    # Get the first task
    if tasks:
        test_task = tasks[0]
        task_id = test_task['task_id']
        
        # Create a mock result
        mock_result = {
            "task_id": task_id,
            "worker_id": "debug-worker",
            "result": {
                "analysis": "This is a debug analysis",
                "components": ["test-component-1", "test-component-2"],
                "reasoning": "Debug reasoning"
            }
        }
        
        print(f"Mock result for task {task_id}:")
        print(json.dumps(mock_result, indent=2))
        
        print("\n💡 To test this manually, POST the above JSON to:")
        print("http://localhost:8000/cards/enhanced-swarm/submit-result/")

if __name__ == "__main__":
    debug_result_submission()
