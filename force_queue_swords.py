#!/usr/bin/env python3
"""Force queue a specific card by UUID, removing any existing job first."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def force_queue_specific_card():
    """Force queue a specific card, removing existing job if needed."""
    target_uuid = "d56255aa-7e1f-4314-be35-dd29f0a52270"
    
    try:
        from cards.models import get_cards_collection
        from cards.job_queue import JobQueue
        
        cards_collection = get_cards_collection()
        job_queue = JobQueue()
        
        print(f"🎯 Force queueing card: {target_uuid}")
        
        # First, find the card
        card = cards_collection.find_one({'uuid': target_uuid})
        if not card:
            print(f"❌ Card with UUID {target_uuid} not found")
            return
            
        card_name = card.get('name', 'Unknown')
        print(f"📄 Found card: {card_name}")
        
        # Check if there's an existing job
        existing_job = job_queue.jobs_collection.find_one({
            'card_uuid': target_uuid,
            'status': {'$in': ['pending', 'processing']}
        })
        
        if existing_job:
            print(f"🗑️ Removing existing job: {existing_job['job_id']}")
            job_queue.jobs_collection.delete_one({'_id': existing_job['_id']})
        
        # Now queue the card with smart prioritization
        job_id = job_queue.enqueue_card_analysis_smart(target_uuid)
        
        if job_id:
            print(f"✅ Successfully queued {card_name} (Job ID: {job_id})")
            
            # Check the job details
            job = job_queue.jobs_collection.find_one({'job_id': job_id})
            if job:
                print(f"📊 Priority: {job.get('priority')}")
                print(f"🎯 Status: {job.get('status')}")
        else:
            print(f"❌ Failed to queue {card_name}")
            
        # Show current queue stats
        stats = job_queue.get_queue_stats()
        print(f"\n📈 Queue Stats:")
        print(f"   Pending: {stats['pending']}")
        print(f"   Processing: {stats['processing']}")
        print(f"   Completed: {stats['completed']}")
        print(f"   Failed: {stats['failed']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_queue_specific_card()
