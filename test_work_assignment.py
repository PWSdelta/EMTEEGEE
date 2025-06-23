#!/usr/bin/env python3
"""
Test Enhanced Swarm Manager Work Assignment
This script tests why the enhanced swarm manager isn't assigning work
"""

import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import EnhancedSwarmManager

def test_work_assignment():
    print("🔍 Testing Enhanced Swarm Manager Work Assignment...")
    
    try:
        # Initialize manager
        manager = EnhancedSwarmManager()
        print("✅ Manager initialized")
        
        # Test worker capabilities
        worker_caps = {
            'hostname': 'test-worker',
            'platform': 'Windows-11',
            'processor': 'AMD',
            'cpu_cores': 12,
            'ram_gb': 64,
            'gpu_available': True,
            'worker_type': 'desktop',
            'specialization': 'fast_gpu_analysis',
            'version': '3.0.0'
        }
        
        # Register a test worker
        worker_id = 'test-worker-123'
        print(f"🔧 Registering worker: {worker_id}")
        
        # Insert worker directly into workers collection
        manager.workers.replace_one(
            {'worker_id': worker_id},
            {
                'worker_id': worker_id,
                'capabilities': worker_caps,
                'status': 'active',
                'last_heartbeat': datetime.now(timezone.utc),
                'tasks_assigned': 0,
                'tasks_completed': 0
            },
            upsert=True
        )
        print("✅ Worker registered")
        
        # Check priority cache
        cache_count = manager.priority_cache.count_documents({})
        print(f"📊 Priority cache size: {cache_count}")
        
        # Get a sample from priority cache
        sample_priorities = list(manager.priority_cache.find().limit(3))
        for priority in sample_priorities:
            print(f"  - Card UUID: {priority.get('card_uuid')}, Priority: {priority.get('priority_score')}")
        
        # Test the complex aggregation pipeline step by step
        print("🔍 Testing aggregation pipeline...")
        
        # Step 1: Just get some priority cache entries
        print("Step 1: Priority cache entries...")
        basic_priorities = list(manager.priority_cache.find().limit(5))
        print(f"  Found {len(basic_priorities)} priority entries")
        
        # Step 2: Test lookup with uuid field
        print("Step 2: Testing lookup with uuid field...")
        try:
            uuid_lookup = list(manager.priority_cache.aggregate([
                {
                    '$lookup': {
                        'from': 'cards',
                        'localField': 'card_uuid',
                        'foreignField': 'uuid',
                        'as': 'card_data'
                    }
                },
                {
                    '$match': {
                        'card_data': {'$ne': []}
                    }
                },
                {
                    '$limit': 3
                }
            ]))
            print(f"  UUID lookup found {len(uuid_lookup)} matches")
            
            if uuid_lookup:
                for match in uuid_lookup:
                    card = match['card_data'][0] if match['card_data'] else {}
                    component_count = card.get('analysis', {}).get('component_count', 0)
                    print(f"    - Card: {card.get('name', 'Unknown')}, Components: {component_count}")
        except Exception as e:
            print(f"  ❌ UUID lookup failed: {e}")
        
        # Step 3: Test lookup with id field
        print("Step 3: Testing lookup with id field...")
        try:
            id_lookup = list(manager.priority_cache.aggregate([
                {
                    '$lookup': {
                        'from': 'cards',
                        'localField': 'card_uuid',
                        'foreignField': 'id',
                        'as': 'card_data'
                    }
                },
                {
                    '$match': {
                        'card_data': {'$ne': []}
                    }
                },
                {
                    '$limit': 3
                }
            ]))
            print(f"  ID lookup found {len(id_lookup)} matches")
            
            if id_lookup:
                for match in id_lookup:
                    card = match['card_data'][0] if match['card_data'] else {}
                    component_count = card.get('analysis', {}).get('component_count', 0)
                    print(f"    - Card: {card.get('name', 'Unknown')}, Components: {component_count}")
        except Exception as e:
            print(f"  ❌ ID lookup failed: {e}")
        
        # Step 4: Test the component count filter
        print("Step 4: Testing component count filter...")
        try:
            incomplete_cards = list(manager.priority_cache.aggregate([
                {
                    '$lookup': {
                        'from': 'cards',
                        'localField': 'card_uuid',
                        'foreignField': 'uuid',
                        'as': 'card_data'
                    }
                },
                {
                    '$match': {
                        'card_data': {'$ne': []},
                        '$or': [
                            {'card_data.analysis.component_count': {'$lt': 20}},
                            {'card_data.analysis.component_count': {'$exists': False}}
                        ]
                    }
                },
                {
                    '$limit': 5
                }
            ]))
            print(f"  Found {len(incomplete_cards)} cards needing analysis")
            
            if incomplete_cards:
                print("  🎯 Cards available for work:")
                for card_match in incomplete_cards:
                    card = card_match['card_data'][0] if card_match['card_data'] else {}
                    component_count = card.get('analysis', {}).get('component_count', 0)
                    print(f"    - {card.get('name', 'Unknown')}: {component_count} components")
            else:
                print("  ❌ No cards found needing analysis")
                
        except Exception as e:
            print(f"  ❌ Component count filter failed: {e}")
        
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_work_assignment()
