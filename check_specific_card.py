#!/usr/bin/env python3
"""Check specific card data."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def check_card():
    """Check specific card data."""
    try:
        from cards.models import get_cards_collection
        from cards.job_queue import JobQueue
        
        cards_collection = get_cards_collection()
        job_queue = JobQueue()
        
        # Check the specific card
        card_uuid = '1f8996c4-1d34-4a98-b1ec-995c18405a11'
        card = cards_collection.find_one({'uuid': card_uuid})
        
        if card:
            print(f"🃏 Card found: {card.get('name', 'Unknown')}")
            print(f"📊 EDHREC fields:")
            
            # Check all possible EDHREC field names
            edhrec_fields = ['edhrecRank', 'edhrecPriorityScore', 'edhrec_rank', 'rank']
            for field in edhrec_fields:
                value = card.get(field)
                if value is not None:
                    print(f"   {field}: {value}")
            
            # Test priority calculation
            priority = job_queue._calculate_smart_priority(card)
            print(f"🎯 Calculated priority: {priority}")
            
            # Show all top-level fields that might be relevant
            print(f"\n📋 All fields containing 'rank' or 'edhrec':")
            for key, value in card.items():
                if 'rank' in key.lower() or 'edhrec' in key.lower():
                    print(f"   {key}: {value}")
                    
        else:
            print(f"❌ Card with UUID {card_uuid} not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_card()
