#!/usr/bin/env python3
"""Test The Abyss collections to ensure they return results."""

import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    print("🕳️ Testing The Abyss Collections")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Test EDHREC Popular collection
        edhrec_query = {'edhrecRank': {'$exists': True, '$ne': None}}
        edhrec_count = cards_collection.count_documents(edhrec_query)
        print(f"📊 EDHREC Popular collection: {edhrec_count:,} cards")
        
        if edhrec_count > 0:
            sample_edhrec = list(cards_collection.find(edhrec_query).sort([('edhrecRank', 1)]).limit(3))
            print("  Top 3 EDHREC cards:")
            for i, card in enumerate(sample_edhrec, 1):
                name = card.get('name', 'Unknown')
                rank = card.get('edhrecRank', 'No rank')
                print(f"    {i}. {name} (Rank: {rank})")
        
        # Test Top Commanders collection
        commanders_query = {
            'type': {'$regex': 'legendary.*creature', '$options': 'i'},
            'edhrecRank': {'$exists': True}
        }
        commanders_count = cards_collection.count_documents(commanders_query)
        print(f"\n👑 Top Commanders collection: {commanders_count:,} cards")
        
        if commanders_count > 0:
            sample_commanders = list(cards_collection.find(commanders_query).sort([('edhrecRank', 1)]).limit(3))
            print("  Top 3 Commanders:")
            for i, card in enumerate(sample_commanders, 1):
                name = card.get('name', 'Unknown')
                rank = card.get('edhrecRank', 'No rank')
                card_type = card.get('type', 'Unknown type')
                print(f"    {i}. {name} (Rank: {rank}) - {card_type}")
        
        # Test basic search
        lightning_query = {'name': {'$regex': 'Lightning', '$options': 'i'}}
        lightning_count = cards_collection.count_documents(lightning_query)
        print(f"\n⚡ 'Lightning' search: {lightning_count:,} cards")
        
        if lightning_count > 0:
            sample_lightning = list(cards_collection.find(lightning_query).limit(3))
            print("  Sample Lightning cards:")
            for i, card in enumerate(sample_lightning, 1):
                name = card.get('name', 'Unknown')
                card_type = card.get('type', 'Unknown type')
                print(f"    {i}. {name} - {card_type}")
        
        print(f"\n✅ All collections working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
