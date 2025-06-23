#!/usr/bin/env python3
"""
Force Worker Model Update
Forces all active workers to refresh their model assignments
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

def force_worker_refresh():
    """Force all workers to refresh their configurations"""
    
    workers_collection = get_mongodb_collection('swarm_workers')
    
    print("🔄 Forcing Worker Model Refresh")
    print("=" * 40)
    
    # Get all workers
    workers = list(workers_collection.find({}))
    
    print("📋 Current worker configurations:")
    for worker in workers:
        worker_id = worker.get('worker_id', 'Unknown')
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        current_model = worker.get('capabilities', {}).get('recommended_model', 'Unknown')
        print(f"   - {worker_id} ({hostname}): {current_model}")
    
    print(f"\n🔄 Forcing configuration refresh...")
    
    # Force workers to refresh by updating their last_heartbeat to trigger re-registration
    refresh_updates = {
        '$set': {
            'force_refresh': True,
            'config_stale': True,
            'last_config_update': datetime.now(timezone.utc),
            'refresh_requested_at': datetime.now(timezone.utc)
        }
    }
    
    result = workers_collection.update_many({}, refresh_updates)
    print(f"✅ Marked {result.modified_count} workers for refresh")
    
    print("\n📋 Workers will now:")
    print("   1. Detect the refresh flag on next heartbeat")
    print("   2. Re-register with server to get new config")
    print("   3. Download correct Llama models")
    print("   4. Start using new model assignments")
    print()
    print("⏰ This should happen within 30 seconds (next heartbeat cycle)")
    print()
    print("🎯 Expected new models:")
    for worker in workers:
        hostname = worker.get('capabilities', {}).get('hostname', '')
        worker_id = worker.get('worker_id', 'Unknown')
        ram_gb = worker.get('capabilities', {}).get('ram_gb', 0)
        
        if 'DESKTOP-2G4707T' in hostname and ram_gb >= 100:
            print(f"   🦣 {worker_id}: → llama3.1:70b")
        elif 'PWS-LP-1235711' in hostname and ram_gb < 20:
            print(f"   💻 {worker_id}: → llama3.2:3b")
        elif 'DESKTOP-F659156' in hostname:
            print(f"   🖥️  {worker_id}: → llama3.1:8b")

if __name__ == '__main__':
    force_worker_refresh()
