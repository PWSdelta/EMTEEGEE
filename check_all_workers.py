#!/usr/bin/env python3
"""
Complete Worker Status Check
Shows all worker data across all collections and statuses
"""

import os
import sys
from datetime import datetime, timezone

# Add the project path so we can import Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')

import django
django.setup()

from cards.models import get_mongodb_collection

def check_all_workers():
    """Check workers across all collections and statuses"""
    
    print("🔍 COMPREHENSIVE WORKER STATUS CHECK")
    print("=" * 60)
    
    # Check main workers collection
    workers_collection = get_mongodb_collection('swarm_workers')
    
    print("📊 Workers Collection (swarm_workers):")
    all_workers = list(workers_collection.find({}))
    print(f"   Total documents: {len(all_workers)}")
    
    for worker in all_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        status = worker.get('status', 'Unknown')
        tasks = worker.get('tasks_completed', 0)
        last_heartbeat = worker.get('last_heartbeat', 'Never')
        print(f"   - {worker_id}")
        print(f"     Host: {hostname}")
        print(f"     Status: {status}")
        print(f"     Tasks: {tasks}")
        print(f"     Last heartbeat: {last_heartbeat}")
        print()
    
    # Also check if there are workers in different statuses
    print("📈 Worker Status Breakdown:")
    statuses = workers_collection.distinct('status')
    for status in statuses:
        count = workers_collection.count_documents({'status': status})
        print(f"   - {status}: {count} workers")
    
    # Check for any worker-related tasks
    tasks_collection = get_mongodb_collection('swarm_tasks')
    
    print(f"\n📋 Recent Task Activity:")
    recent_tasks = list(tasks_collection.find({}).sort([('created_at', -1)]).limit(5))
    if recent_tasks:
        for task in recent_tasks:
            worker_id = task.get('assigned_to', 'Unassigned')
            card_name = task.get('card_name', 'Unknown')
            status = task.get('status', 'Unknown')
            created = task.get('created_at', 'Unknown')
            print(f"   - {card_name} → {worker_id} ({status}) at {created}")
    else:
        print("   No recent tasks found")
    
    # Check unique worker IDs that have been assigned tasks
    print(f"\n👥 Unique Workers That Have Done Tasks:")
    worker_ids = tasks_collection.distinct('assigned_to')
    worker_ids = [w for w in worker_ids if w]  # Remove None values
    
    for worker_id in worker_ids:
        task_count = tasks_collection.count_documents({'assigned_to': worker_id})
        completed_count = tasks_collection.count_documents({
            'assigned_to': worker_id, 
            'status': 'completed'
        })
        print(f"   - {worker_id}: {completed_count}/{task_count} tasks completed")
    
    # Check if there might be workers in other collections
    db = workers_collection.database
    collection_names = db.list_collection_names()
    
    print(f"\n🗃️  All Collections in Database:")
    for name in collection_names:
        if 'worker' in name.lower() or 'swarm' in name.lower():
            count = db[name].count_documents({})
            print(f"   - {name}: {count} documents")
    
    # Try to find workers by searching for documents with worker_id field
    print(f"\n🔎 Searching All Collections for worker_id Field:")
    for collection_name in collection_names:
        try:
            collection = db[collection_name]
            worker_docs = list(collection.find({'worker_id': {'$exists': True}}).limit(3))
            if worker_docs:
                print(f"   - {collection_name}: {len(worker_docs)} docs with worker_id")
                for doc in worker_docs[:2]:  # Show first 2
                    worker_id = doc.get('worker_id', 'Unknown')
                    print(f"     → {worker_id}")
        except Exception as e:
            # Skip collections that might have issues
            pass

if __name__ == '__main__':
    check_all_workers()
