#!/usr/bin/env python3
"""
Debug script to examine task structure and identify field mismatches
"""

import os
import sys
import django
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings
from pymongo import MongoClient

def debug_task_structure():
    """Debug task structure to understand field naming"""
    print("🔍 Examining task structure...")
      # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emteegee_dev']
    
    # Get recent tasks
    tasks = list(db.enhanced_swarm_tasks.find().sort('_id', -1).limit(3))
    
    print(f"📋 Found {len(tasks)} recent tasks")
    
    for i, task in enumerate(tasks):
        print(f"\n📝 Task {i+1}:")
        print("Available fields:")
        for key in task.keys():
            print(f"  {key}: {type(task[key])}")
        
        print("\nFull task structure:")
        pprint(task, width=120)
        
        # Check if this is a completed task with results
        if 'status' in task:
            print(f"\nTask status: {task['status']}")
        if 'result' in task:
            print(f"Has result: {bool(task['result'])}")
        
        print("-" * 80)

if __name__ == "__main__":
    debug_task_structure()
