#!/usr/bin/env python3
"""
Worker Database Cleanup Script
Removes test workers and fixes model assignments for real machines
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

def cleanup_workers():
    """Clean up fake workers and fix real worker configurations"""
    
    workers_collection = get_mongodb_collection('swarm_workers')
    
    print("🔍 Current workers in database:")
    all_workers = list(workers_collection.find({}))
    for i, worker in enumerate(all_workers, 1):
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        tasks_completed = worker.get('tasks_completed', 0)
        print(f"{i}. {worker_id} (Host: {hostname}) - {tasks_completed} tasks")
    
    print(f"\n📊 Total workers found: {len(all_workers)}")
    
    # Define your 3 real machines
    real_machines = {
        'DESKTOP-F659156',    # Desktop with RTX 3070
        'DESKTOP-2G4707T',    # Beefy laptop with 128GB RAM  
        'PWS-LP-1235711'      # Another machine
    }
    
    # Find fake/test workers
    fake_workers = []
    real_workers = []
    
    for worker in all_workers:
        hostname = worker.get('capabilities', {}).get('hostname', '')
        worker_id = worker.get('worker_id', '')
        
        # Check if this is a test worker or not from your real machines
        is_real = False
        for real_hostname in real_machines:
            if real_hostname in hostname or real_hostname in worker_id:
                is_real = True
                break
        
        if is_real:
            real_workers.append(worker)
        else:
            fake_workers.append(worker)
    
    print(f"\n✅ Real workers (keeping): {len(real_workers)}")
    for worker in real_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        tasks = worker.get('tasks_completed', 0)
        print(f"   - {worker_id} ({hostname}) - {tasks} tasks")
    
    print(f"\n🗑️  Fake/test workers (will delete): {len(fake_workers)}")
    for worker in fake_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')  
        worker_id = worker.get('worker_id', 'Unknown')
        print(f"   - {worker_id} ({hostname})")
    
    if fake_workers:
        print(f"\n⚠️  About to delete {len(fake_workers)} fake workers.")
        confirm = input("Type 'yes' to proceed with cleanup: ").strip().lower()
        
        if confirm == 'yes':
            # Delete fake workers
            fake_ids = [w['_id'] for w in fake_workers]
            result = workers_collection.delete_many({'_id': {'$in': fake_ids}})
            print(f"✅ Deleted {result.deleted_count} fake workers")
            
            # Update real workers with correct model assignments
            print("\n🔧 Fixing model assignments for real workers...")
            
            for worker in real_workers:
                hostname = worker.get('capabilities', {}).get('hostname', '')
                ram_gb = worker.get('capabilities', {}).get('ram_gb', 0)
                worker_id = worker.get('worker_id', '')
                
                updates = {}
                
                # Fix the 128GB laptop to use big models
                if 'DESKTOP-2G4707T' in hostname and ram_gb >= 100:
                    updates = {
                        '$set': {
                            'capabilities.recommended_model': 'llama3.1:70b',
                            'capabilities.alternative_models': ['mixtral:8x7b', 'llama3.1:70b'],
                            'capabilities.model_preference': 'large',
                            'capabilities.specialization': 'deep_cpu_analysis',
                            'capabilities.worker_type': 'laptop_powerhouse'
                        }
                    }
                    print(f"   📱 Fixed laptop {hostname}: Now uses big models (70B/Mixtral)")
                
                # Ensure desktop workers use appropriate models
                elif 'gpu_available' in worker.get('capabilities', {}) and worker['capabilities']['gpu_available']:
                    updates = {
                        '$set': {
                            'capabilities.recommended_model': 'qwen2.5:7b',
                            'capabilities.alternative_models': ['llama3.1:8b', 'qwen2.5:7b'],
                            'capabilities.model_preference': 'fast',
                            'capabilities.specialization': 'fast_gpu_analysis'
                        }
                    }
                    print(f"   🖥️  Fixed desktop {hostname}: Uses fast GPU models")
                
                if updates:
                    workers_collection.update_one(
                        {'_id': worker['_id']}, 
                        updates
                    )
            
            print("✅ Worker cleanup completed!")
            
        else:
            print("❌ Cleanup cancelled")
    else:
        print("✅ No fake workers found - database is clean!")
    
    # Show final status
    print(f"\n📊 Final worker count:")
    final_workers = list(workers_collection.find({}))
    for worker in final_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        tasks = worker.get('tasks_completed', 0)
        model = worker.get('capabilities', {}).get('recommended_model', 'Unknown')
        print(f"   - {worker_id} ({hostname}) - {tasks} tasks - Model: {model}")
    
    print(f"\n🎉 Total active workers: {len(final_workers)}")

if __name__ == '__main__':
    print("🐝 EMTEEGEE Worker Database Cleanup")
    print("=" * 50)
    cleanup_workers()
