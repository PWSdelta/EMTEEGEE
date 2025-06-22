#!/usr/bin/env python3
"""Check the EDHREC data for queued cards."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def check_edhrec_data():
    """Check the actual EDHREC data in our cards."""
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        
        # Get Sol Ring specifically
        sol_ring = cards_collection.find_one({'name': 'Sol Ring'})
        
        if sol_ring:
            print("🔍 Sol Ring data:")
            print(f"  UUID: {sol_ring.get('uuid')}")
            print(f"  Name: {sol_ring.get('name')}")
            print(f"  edhrecRank: {sol_ring.get('edhrecRank')}")
            print(f"  edhrec_rank: {sol_ring.get('edhrec_rank')}")
            print(f"  edhrecPriorityScore: {sol_ring.get('edhrecPriorityScore')}")
            
            # Show all keys that contain 'edhrec'
            edhrec_keys = [k for k in sol_ring.keys() if 'edhrec' in k.lower()]
            print(f"  All EDHREC-related keys: {edhrec_keys}")
            
            # Test priority calculation
            from cards.job_queue import job_queue
            priority = job_queue._calculate_smart_priority(sol_ring)
            print(f"  Calculated priority: {priority}")
        else:
            print("❌ Sol Ring not found!")
            
        # Check a few more cards
        top_cards = list(cards_collection.find(
            {'name': {'$in': ['Command Tower', 'Arcane Signet']}},
            {'name': 1, 'edhrecRank': 1, 'edhrec_rank': 1, 'edhrecPriorityScore': 1}
        ))
        
        print(f"\n🔍 Other top cards:")
        for card in top_cards:
            name = card.get('name')
            rank = card.get('edhrecRank')
            rank2 = card.get('edhrec_rank')
            score = card.get('edhrecPriorityScore')
            print(f"  {name}: edhrecRank={rank}, edhrec_rank={rank2}, score={score}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_edhrec_data()
