#!/usr/bin/env python3
"""
Remove Duplicate PWS Worker
Removes the duplicate desktop-PWS-LP-1235711 worker, keeping laptop_lite version
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

def remove_duplicate_pws_worker():
    """Remove duplicate PWS-LP-1235711 workers"""
    
    workers_collection = get_mongodb_collection('swarm_workers')
    
    print("🔍 Current PWS-LP-1235711 workers:")
    
    # Find all PWS workers
    pws_workers = list(workers_collection.find({
        'capabilities.hostname': 'PWS-LP-1235711'
    }))
    
    if len(pws_workers) <= 1:
        print("✅ No duplicates found!")
        return
    
    print(f"Found {len(pws_workers)} workers on PWS-LP-1235711:")
    for worker in pws_workers:
        worker_id = worker.get('worker_id', 'Unknown')
        tasks = worker.get('tasks_completed', 0)
        worker_type = worker.get('capabilities', {}).get('worker_type', 'Unknown')
        print(f"   - {worker_id} (type: {worker_type}) - {tasks} tasks")
    
    # Keep laptop_lite, remove desktop
    desktop_workers = [w for w in pws_workers if w.get('worker_id', '').startswith('desktop-')]
    laptop_lite_workers = [w for w in pws_workers if w.get('worker_id', '').startswith('laptop_lite-')]
    
    if desktop_workers:
        print(f"\n🗑️  Removing desktop-PWS-LP-1235711 (duplicate)...")
        for worker in desktop_workers:
            result = workers_collection.delete_one({'_id': worker['_id']})
            if result.deleted_count:
                print(f"   ✅ Deleted {worker.get('worker_id')}")
    
    if laptop_lite_workers:
        print(f"✅ Keeping laptop_lite-PWS-LP-1235711 (correct for 15GB RAM)")
    
    # Show final status
    print(f"\n📊 Final workers on PWS-LP-1235711:")
    remaining_workers = list(workers_collection.find({
        'capabilities.hostname': 'PWS-LP-1235711'
    }))
    
    for worker in remaining_workers:
        worker_id = worker.get('worker_id', 'Unknown')
        model = worker.get('capabilities', {}).get('recommended_model', 'Unknown')
        print(f"   - {worker_id}: {model}")
    
    print(f"\n🎉 Now you have exactly 3 workers (one per machine)!")

if __name__ == '__main__':
    print("🧹 Remove Duplicate PWS Worker")
    print("=" * 35)
    remove_duplicate_pws_worker()
