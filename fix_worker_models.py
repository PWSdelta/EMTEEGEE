#!/usr/bin/env python3
"""
Fix Worker Model Assignments
Corrects model assignments and removes duplicate workers
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

def fix_worker_models():
    """Fix model assignments and remove duplicates"""
    
    workers_collection = get_mongodb_collection('swarm_workers')
    
    print("🔍 Current workers:")
    all_workers = list(workers_collection.find({}))
    for worker in all_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        tasks = worker.get('tasks_completed', 0)
        ram_gb = worker.get('capabilities', {}).get('ram_gb', 0)
        model = worker.get('capabilities', {}).get('recommended_model', 'Unknown')
        print(f"   - {worker_id} ({hostname}) - {tasks} tasks - {ram_gb}GB RAM - Model: {model}")
    
    # Find duplicate PWS-LP-1235711 workers
    pws_workers = [w for w in all_workers if 'PWS-LP-1235711' in w.get('capabilities', {}).get('hostname', '')]
    
    if len(pws_workers) > 1:
        print(f"\n🗑️  Found {len(pws_workers)} workers on PWS-LP-1235711:")
        for worker in pws_workers:
            worker_id = worker.get('worker_id', 'Unknown')
            tasks = worker.get('tasks_completed', 0)
            print(f"   - {worker_id} - {tasks} tasks")
        
        # Keep the one with more tasks completed
        keeper = max(pws_workers, key=lambda w: w.get('tasks_completed', 0))
        duplicates = [w for w in pws_workers if w['_id'] != keeper['_id']]
        
        print(f"\n✅ Keeping: {keeper.get('worker_id')} ({keeper.get('tasks_completed', 0)} tasks)")
        print(f"🗑️  Removing {len(duplicates)} duplicates:")
        
        for dup in duplicates:
            print(f"   - {dup.get('worker_id')} ({dup.get('tasks_completed', 0)} tasks)")
        
        confirm = input("\nRemove duplicate workers? (yes/no): ").strip().lower()
        if confirm == 'yes':
            duplicate_ids = [d['_id'] for d in duplicates]
            result = workers_collection.delete_many({'_id': {'$in': duplicate_ids}})
            print(f"✅ Deleted {result.deleted_count} duplicate workers")
        else:
            print("❌ Skipping duplicate removal")
    
    # Now fix model assignments for remaining workers
    print("\n🔧 Fixing model assignments...")
    
    current_workers = list(workers_collection.find({}))
    
    for worker in current_workers:
        hostname = worker.get('capabilities', {}).get('hostname', '')
        worker_id = worker.get('worker_id', '')
        ram_gb = worker.get('capabilities', {}).get('ram_gb', 0)
        
        updates = None
        
        # Fix laptop beast (128GB RAM) - should use BIG models
        if 'DESKTOP-2G4707T' in hostname and ram_gb >= 100:
            updates = {
                '$set': {
                    'capabilities.recommended_model': 'llama3.1:70b',
                    'capabilities.alternative_models': ['mixtral:8x7b', 'llama3.1:70b', 'llama3.2:90b'],
                    'capabilities.model_preference': 'massive',
                    'capabilities.specialization': 'deep_analysis_powerhouse',
                    'capabilities.worker_type': 'laptop_beast'
                }
            }
            print(f"   🦣 Fixed BEAST laptop {hostname}: Now uses MASSIVE models (70B+)")
        
        # Fix small laptop (15GB RAM) - should use small models
        elif 'PWS-LP-1235711' in hostname and ram_gb < 20:
            updates = {
                '$set': {
                    'capabilities.recommended_model': 'llama3.2:3b',
                    'capabilities.alternative_models': ['llama3.2:1b', 'llama3.2:3b', 'qwen2.5:7b'],
                    'capabilities.model_preference': 'lightweight',
                    'capabilities.specialization': 'lightweight_analysis',
                    'capabilities.worker_type': 'laptop_lite'
                }
            }
            print(f"   💻 Fixed small laptop {hostname}: Now uses SMALL models (3B)")
        
        # Fix desktop with GPU - fast models
        elif 'DESKTOP-F659156' in hostname:
            updates = {
                '$set': {
                    'capabilities.recommended_model': 'qwen2.5:7b',
                    'capabilities.alternative_models': ['llama3.1:8b', 'qwen2.5:7b', 'qwen2.5:14b'],
                    'capabilities.model_preference': 'fast_gpu',
                    'capabilities.specialization': 'fast_gpu_analysis',
                    'capabilities.worker_type': 'desktop_gpu'
                }
            }
            print(f"   🖥️  Fixed desktop {hostname}: Uses FAST GPU models")
        
        if updates:
            workers_collection.update_one({'_id': worker['_id']}, updates)
    
    # Show final results
    print(f"\n📊 Final worker configuration:")
    final_workers = list(workers_collection.find({}))
    
    for worker in final_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        tasks = worker.get('tasks_completed', 0)
        ram_gb = worker.get('capabilities', {}).get('ram_gb', 0)
        model = worker.get('capabilities', {}).get('recommended_model', 'Unknown')
        worker_type = worker.get('capabilities', {}).get('worker_type', 'Unknown')
        
        print(f"   - {worker_id}")
        print(f"     Host: {hostname} ({ram_gb}GB RAM)")
        print(f"     Type: {worker_type}")
        print(f"     Model: {model}")
        print(f"     Tasks: {tasks}")
        print()
    
    print(f"🎉 Total workers: {len(final_workers)}")
    print("✅ Model assignments fixed!")

if __name__ == '__main__':
    print("🔧 EMTEEGEE Worker Model Fix")
    print("=" * 40)
    fix_worker_models()
