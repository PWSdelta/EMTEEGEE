#!/usr/bin/env python
"""
Analyze the job queue to see if smart prioritization is working.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection
from cards.job_queue import JobQueue

def analyze_queue_priorities():
    """Analyze the current job queue to see prioritization in action."""
    print("🔍 Job Queue Priority Analysis")
    print("=" * 60)
    
    try:
        cards_collection = get_cards_collection()
        job_queue = JobQueue()
        
        # Get queue statistics
        stats = job_queue.get_queue_stats()
        print(f"📊 Queue Stats:")
        for status, count in stats.items():
            print(f"  - {status.title()}: {count}")
        
        # Get recent jobs to see their priorities
        recent_jobs = job_queue.get_recent_jobs(limit=10)
        print(f"\n📋 Recent Jobs (Last 10):")
        
        for job in recent_jobs:
            card_uuid = job['card_uuid']
            priority = job['priority']
            status = job['status']
            created_at = job['created_at']
            
            # Get card info to understand why it got this priority
            card = cards_collection.find_one(
                {'uuid': card_uuid},
                {'name': 1, 'analysis.components': 1, 'edhrecPriorityScore': 1, 'prices.usd': 1}
            )
            
            if card:
                name = card.get('name', 'Unknown')
                components = card.get('analysis', {}).get('components', {})
                completed_count = sum(1 for comp in components.values() if comp is not None) if components else 0
                edhrec_score = card.get('edhrecPriorityScore', 0)
                
                print(f"\n🃏 {name}")
                print(f"   UUID: {card_uuid[:8]}...")
                print(f"   Priority: {priority}")
                print(f"   Status: {status}")
                print(f"   Components: {completed_count}/20")
                print(f"   EDHREC: {edhrec_score}")
                print(f"   Created: {created_at}")
            else:
                print(f"\n❌ Card not found: {card_uuid[:8]}... (Priority: {priority}, Status: {status})")
        
        # Check for high priority jobs specifically
        print(f"\n🎯 High Priority Analysis:")
        
        # Get jobs sorted by priority
        high_priority_jobs = list(job_queue.jobs_collection.find(
            {"status": {"$in": ["pending", "processing"]}},
            {"card_uuid": 1, "priority": 1, "status": 1}
        ).sort("priority", -1).limit(5))
        
        if high_priority_jobs:
            print(f"Top 5 Priority Jobs:")
            for i, job in enumerate(high_priority_jobs, 1):
                card_uuid = job['card_uuid']
                priority = job['priority']
                status = job['status']
                
                # Get card completion info
                card = cards_collection.find_one(
                    {'uuid': card_uuid},
                    {'name': 1, 'analysis.components': 1}
                )
                
                if card:
                    name = card.get('name', 'Unknown')
                    components = card.get('analysis', {}).get('components', {})
                    completed_count = sum(1 for comp in components.values() if comp is not None) if components else 0
                    
                    print(f"  {i}. {name} | Priority: {priority} | Components: {completed_count}/20 | {status}")
                else:
                    print(f"  {i}. [Card not found] | Priority: {priority} | {status}")
        else:
            print("No pending/processing jobs found")
        
        # Check if there are any cards with partial completion that should be prioritized
        print(f"\n🔍 Checking for Partially Completed Cards:")
        
        partial_cards = list(cards_collection.find(
            {
                'analysis.components': {'$exists': True},
                'analysis.fully_analyzed': {'$ne': True}
            },
            {'uuid': 1, 'name': 1, 'analysis.components': 1}
        ).limit(5))
        
        if partial_cards:
            print(f"Found {len(partial_cards)} partially completed cards:")
            for card in partial_cards:
                name = card.get('name', 'Unknown')
                components = card.get('analysis', {}).get('components', {})
                completed_count = sum(1 for comp in components.values() if comp is not None) if components else 0
                
                # Check if this card has a job in queue
                existing_job = job_queue.jobs_collection.find_one({
                    'card_uuid': card['uuid'],
                    'status': {'$in': ['pending', 'processing']}
                })
                
                job_status = "In queue" if existing_job else "Not queued"
                job_priority = existing_job.get('priority', 'N/A') if existing_job else 'N/A'
                
                print(f"  - {name}: {completed_count}/20 components | {job_status} | Priority: {job_priority}")
        else:
            print("No partially completed cards found")
        
        print(f"\n✅ Priority analysis complete!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_queue_priorities()
