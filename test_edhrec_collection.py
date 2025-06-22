#!/usr/bin/env python3
"""
Test script for the EDHREC collection functionality.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    print("🏆 Testing EDHREC Collection Functionality")
    print("=" * 60)
    
    cards_collection = get_cards_collection()
    
    # Test the EDHREC collection query
    print("🔍 Testing EDHREC collection query...")
    
    # This mirrors the query from the_abyss view for collection='edhrec'
    query = {'edhrecRank': {'$exists': True, '$ne': None}}
    sort_criteria = [('edhrecRank', 1)]  # Most popular first (lowest rank number)
    
    # Get top 10 cards by EDHREC rank
    top_cards = list(cards_collection.find(query).sort(sort_criteria).limit(10))
    
    print(f"📊 Found {len(top_cards)} cards in top 10:")
    print()
    
    for i, card in enumerate(top_cards, 1):
        name = card.get('name', 'Unknown')
        rank = card.get('edhrecRank', 'N/A')
        card_type = card.get('type', 'Unknown')
        uuid = card.get('uuid', 'N/A')
        
        print(f"{i:2}. #{rank:>6} - {name}")
        print(f"     Type: {card_type}")
        print(f"     UUID: {uuid}")
        print()
    
    # Test total count
    total_count = cards_collection.count_documents(query)
    print(f"📈 Total cards with EDHREC ranks: {total_count:,}")
    
    # Test URL construction
    print(f"\n🌐 Direct URL: http://localhost:8000/abyss/?collection=edhrec")
    
    print(f"\n✨ EDHREC collection test complete!")

if __name__ == '__main__':
    main()
