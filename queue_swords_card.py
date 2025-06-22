#!/usr/bin/env python3
"""Queue specific Swords to Plowshares card for analysis."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def queue_swords_card():
    """Queue the specific Swords to Plowshares card."""
    try:
        from cards.models import get_cards_collection
        from cards.job_queue import JobQueue
        
        cards_collection = get_cards_collection()
        job_queue = JobQueue()
        
        # Target the specific UUID
        target_uuid = 'd56255aa-7e1f-4314-be35-dd29f0a52270'
        
        print(f"🎯 Looking for card with UUID: {target_uuid}")
        
        card = cards_collection.find_one({'uuid': target_uuid})
        
        if card:
            print(f"✅ Found card: {card.get('name', 'Unknown')}")
            print(f"📊 EDHREC Rank: #{card.get('edhrecRank', 'Unknown')}")
            
            # Calculate priority
            priority = job_queue._calculate_smart_priority(card)
            print(f"🎯 Calculated Priority: {priority}")
            
            # Queue the card
            job_id = job_queue.enqueue_card_analysis_smart(target_uuid)
            if job_id:
                print(f"✅ Successfully queued card! Job ID: {job_id}")
            else:
                print("❌ Failed to queue card")
                
        else:
            print(f"❌ Card not found with UUID: {target_uuid}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    queue_swords_card()
