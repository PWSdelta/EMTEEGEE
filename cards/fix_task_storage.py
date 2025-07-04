#!/usr/bin/env python3
"""
Fix task storage issue in enhanced swarm manager
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def check_task_storage():
    print("🔍 CHECKING TASK STORAGE ISSUE")
    print("=" * 50)
    
    # Check if tasks collection exists and has data
    if hasattr(enhanced_swarm, 'tasks'):
        print("✅ Enhanced swarm has tasks collection")
        
        # Count total tasks
        total_tasks = enhanced_swarm.tasks.count_documents({})
        print(f"📊 Total tasks in database: {total_tasks}")
        
        # Show recent tasks
        recent_tasks = list(enhanced_swarm.tasks.find({}).sort('created_at', -1).limit(10))
        print(f"📋 Recent tasks:")
        
        for task in recent_tasks:
            print(f"   - {task.get('task_id', 'no_id')}: {task.get('status', 'no_status')} ({task.get('worker_id', 'no_worker')})")
    else:
        print("❌ Enhanced swarm has no tasks collection")
    
    # Test get_work to see if it stores tasks properly
    print("\n🧪 TESTING GET_WORK TASK STORAGE")
    
    work = enhanced_swarm.get_work("test_worker_123")
    
    if work and 'task_id' in work:
        task_id = work['task_id']
        print(f"✅ get_work returned task_id: {task_id}")
        
        # Check if task was stored
        stored_task = enhanced_swarm.tasks.find_one({'task_id': task_id})
        
        if stored_task:
            print(f"✅ Task {task_id} was properly stored in database")
            print(f"   Status: {stored_task.get('status', 'unknown')}")
            print(f"   Worker: {stored_task.get('worker_id', 'unknown')}")
        else:
            print(f"❌ Task {task_id} was NOT stored in database")
            print("   This is why submit_task_result fails!")
    else:
        print("❌ get_work returned no task_id")

if __name__ == "__main__":
    check_task_storage()