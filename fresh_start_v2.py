#!/usr/bin/env python3
"""
EMTEEGEE Analysis Fresh Start Script v2.0
Resets all analysis data and sets up consistent Llama-only model assignments
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

def fresh_start_analysis():
    """Complete fresh start for v2.0 analysis system"""
    
    print("🚀 EMTEEGEE Analysis System v2.0 Fresh Start")
    print("=" * 60)
    print("This will:")
    print("   🗑️  Delete ALL existing analysis data")
    print("   🔧 Set pure Llama model assignments")
    print("   🧹 Clear all task queues")
    print("   🎯 Prepare for consistent, high-quality analysis")
    print()
    
    # Get collections
    cards_collection = get_mongodb_collection('cards')
    workers_collection = get_mongodb_collection('swarm_workers')
    tasks_collection = get_mongodb_collection('swarm_tasks')
    
    # Show current status
    total_cards = cards_collection.count_documents({})
    analyzed_cards = cards_collection.count_documents({'analysis.fully_analyzed': True})
    total_tasks = tasks_collection.count_documents({})
    total_workers = workers_collection.count_documents({})
    
    print(f"📊 Current Status:")
    print(f"   - Total cards: {total_cards:,}")
    print(f"   - Analyzed cards: {analyzed_cards:,}")
    print(f"   - Tasks in queue: {total_tasks:,}")
    print(f"   - Active workers: {total_workers}")
    print()
    
    # Confirm the reset
    print("⚠️  WARNING: This will permanently delete all existing analysis data!")
    print("   You'll lose all current card analysis results.")
    print("   But you'll get much better, consistent results with v2.0!")
    print()
    
    confirm1 = input("Are you sure you want to proceed? (type 'DELETE ALL' to confirm): ").strip()
    if confirm1 != 'DELETE ALL':
        print("❌ Fresh start cancelled")
        return
    
    confirm2 = input("Final confirmation - Reset everything for v2.0? (yes/no): ").strip().lower()
    if confirm2 != 'yes':
        print("❌ Fresh start cancelled")
        return
    
    print("\n🧹 Starting fresh reset...")
    
    # Step 1: Clear all analysis data from cards
    print("1️⃣  Clearing analysis data from cards...")
    result = cards_collection.update_many(
        {},
        {
            '$unset': {
                'analysis': '',
                'fully_analyzed': '',
                'analysis_version': '',
                'last_analyzed': ''
            }
        }
    )
    print(f"   ✅ Cleared analysis from {result.modified_count:,} cards")
    
    # Step 2: Delete all tasks
    print("2️⃣  Clearing task queue...")
    result = tasks_collection.delete_many({})
    print(f"   ✅ Deleted {result.deleted_count:,} tasks")
    
    # Step 3: Reset worker task counters and set Llama models
    print("3️⃣  Configuring workers for v2.0 (Llama-only)...")
    
    workers = list(workers_collection.find({}))
    for worker in workers:
        hostname = worker.get('capabilities', {}).get('hostname', '')
        ram_gb = worker.get('capabilities', {}).get('ram_gb', 0)
        worker_id = worker.get('worker_id', 'Unknown')
        
        # Reset task counters
        reset_updates = {
            '$set': {
                'tasks_completed': 0,
                'tasks_failed': 0,
                'tasks_today': 0,
                'active_tasks': 0,
                'analysis_version': '2.0',
                'last_reset': datetime.now(timezone.utc)
            }
        }
          # Configure Llama models based on hardware
        if 'DESKTOP-2G4707T' in hostname and ram_gb >= 100:
            # Beast laptop: 128GB RAM → Llama 3.3 70B (new efficient model!)
            reset_updates['$set'].update({
                'capabilities.recommended_model': 'llama3.3:70b',
                'capabilities.alternative_models': [],
                'capabilities.model_family': 'llama',
                'capabilities.model_size': '70b',
                'capabilities.specialization': 'deep_analysis',
                'capabilities.worker_type': 'beast_laptop',
                'capabilities.analysis_style': 'comprehensive'
            })
            print(f"   🦣 {worker_id}: Llama 3.3 70B (405B-Level Performance!)")
            
        elif 'PWS-LP-1235711' in hostname and ram_gb < 20:
            # Lite laptop: 15GB RAM → Llama 3.2 3B
            reset_updates['$set'].update({
                'capabilities.recommended_model': 'llama3.2:3b',
                'capabilities.alternative_models': [],
                'capabilities.model_family': 'llama',
                'capabilities.model_size': '3b',
                'capabilities.specialization': 'efficient_analysis',
                'capabilities.worker_type': 'lite_laptop',
                'capabilities.analysis_style': 'concise'
            })
            print(f"   💻 {worker_id}: Llama 3.2 3B (Efficient Analysis)")
            
        elif 'DESKTOP-F659156' in hostname:
            # Desktop GPU: 64GB RAM → Llama 3.1 8B
            reset_updates['$set'].update({
                'capabilities.recommended_model': 'llama3.1:8b',
                'capabilities.alternative_models': [],
                'capabilities.model_family': 'llama',
                'capabilities.model_size': '8b',
                'capabilities.specialization': 'balanced_analysis',
                'capabilities.worker_type': 'desktop_gpu',
                'capabilities.analysis_style': 'balanced'
            })
            print(f"   🖥️  {worker_id}: Llama 3.1 8B (Balanced Analysis)")
        
        # Apply the updates
        workers_collection.update_one({'_id': worker['_id']}, reset_updates)
    
    # Step 4: Create fresh priority cache
    print("4️⃣  Rebuilding priority cache...")
    priority_cache = get_mongodb_collection('priority_cache')
    priority_cache.delete_many({})
    
    # Add high-priority cards (low EDHREC rank) to priority cache
    high_priority_cards = cards_collection.find({
        'edhrecRank': {'$lt': 1000, '$exists': True}
    }).limit(5000)
    
    priority_docs = []
    for card in high_priority_cards:
        priority_score = max(0.1, min(1.0, 1.0 - (card.get('edhrecRank', 10000) / 10000)))
        priority_docs.append({
            'card_uuid': card['uuid'],
            'priority_score': priority_score,
            'edhrec_rank': card.get('edhrecRank'),
            'created_at': datetime.now(timezone.utc)
        })
    
    if priority_docs:
        priority_cache.insert_many(priority_docs)
        print(f"   ✅ Added {len(priority_docs):,} high-priority cards to cache")
    
    # Step 5: Final status
    print("\n🎉 Fresh Start Complete!")
    print("=" * 40)
    
    final_workers = list(workers_collection.find({}))
    print("📊 v2.0 Worker Configuration:")
    for worker in final_workers:
        hostname = worker.get('capabilities', {}).get('hostname', 'Unknown')
        worker_id = worker.get('worker_id', 'Unknown')
        model = worker.get('capabilities', {}).get('recommended_model', 'Unknown')
        style = worker.get('capabilities', {}).get('analysis_style', 'Unknown')
        
        print(f"   - {worker_id}")
        print(f"     Host: {hostname}")
        print(f"     Model: {model}")
        print(f"     Style: {style}")
        print()
    
    print("✅ Ready for v2.0 Analysis!")
    print("📋 Next Steps:")
    print("   1. Restart all workers to pick up new model assignments")
    print("   2. Workers will download correct Llama models")
    print("   3. Begin fresh, consistent analysis of all cards")
    print("   4. Enjoy superior quality and consistent voice!")
    print()
    print("🎯 All 29,448+ cards will now be analyzed with consistent")
    print("   Llama models for unified voice and style!")

if __name__ == '__main__':
    fresh_start_analysis()
