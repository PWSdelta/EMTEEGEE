#!/usr/bin/env python3
"""Force queue some cards to test EDHREC prioritization."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def force_queue_test():
    """Force queue some high-priority cards to test the system."""
    try:
        from cards.models import get_cards_collection
        from cards.job_queue import job_queue
        
        cards_collection = get_cards_collection()
        
        print('🎯 Finding high-priority cards to test prioritization...')
        
        # Find some cards with different EDHREC ranks
        test_cards = list(cards_collection.find(
            {
                'edhrecRank': {'$exists': True, '$ne': None},
                'analysis.fully_analyzed': {'$ne': True}
            },
            {'uuid': 1, 'name': 1, 'edhrecRank': 1}
        ).sort('edhrecRank', 1).limit(10))  # Get top 10 EDHREC cards
        
        print(f'📊 Found {len(test_cards)} cards for testing:')
        
        jobs_added = 0
        for card in test_cards:
            name = card.get('name', 'Unknown')
            rank = card.get('edhrecRank', 999999)
            uuid = card.get('uuid')
            
            # Calculate priority using our new system
            priority = job_queue._calculate_smart_priority(card)
            
            try:
                job_id = job_queue.enqueue_card_analysis_smart(uuid)
                if job_id:
                    jobs_added += 1
                    print(f'  ✅ {name} (Rank #{rank}) → Priority {priority}')
                else:
                    print(f'  ⚠️ {name} (Rank #{rank}) → Already queued')
            except Exception as e:
                print(f'  ❌ {name} (Rank #{rank}) → Error: {e}')
        
        print(f'\n✅ Added {jobs_added} jobs to the queue')
        
        # Show queue stats
        stats = job_queue.get_queue_stats()
        print(f"📊 Queue Stats: {stats}")
        
        # Show first few jobs to verify priority ordering
        jobs = list(job_queue.jobs_collection.find(
            {'status': 'pending'}, 
            {'card_uuid': 1, 'priority': 1, 'created_at': 1}
        ).sort([('priority', -1), ('created_at', 1)]).limit(5))
        
        print(f"\n🏆 Top 5 prioritized jobs:")
        for i, job in enumerate(jobs, 1):
            card_uuid = job.get('card_uuid')
            priority = job.get('priority')
            # Look up card name
            card = cards_collection.find_one({'uuid': card_uuid}, {'name': 1, 'edhrecRank': 1})
            name = card.get('name', 'Unknown') if card else 'Unknown'
            rank = card.get('edhrecRank', 'N/A') if card else 'N/A'
            print(f"  {i}. {name} (Rank #{rank}) → Priority {priority}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_queue_test()
