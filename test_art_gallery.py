#!/usr/bin/env python3
"""Test the art gallery functionality."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    print("🎨 Testing Art Gallery Functionality")
    print("=" * 50)
    
    cards_collection = get_cards_collection()
      # Test the art gallery query
    query = {
        'imageUris.art_crop': {'$exists': True, '$ne': None},
        '$or': [
            {'rarity': {'$in': ['mythic', 'rare']}},
            {'type': {'$regex': 'Planeswalker', '$options': 'i'}},
            {'edhrecRank': {'$lte': 1000}},
        ]
    }
    
    total_count = cards_collection.count_documents(query)
    print(f"📊 Cards available for art gallery: {total_count:,}")
      # Get a sample of cards
    sample_cards = list(cards_collection.find(
        query, 
        {'name': 1, 'artist': 1, 'imageUris.art_crop': 1, 'rarity': 1, 'type': 1}
    ).limit(10))
    
    print(f"\n🖼️ Sample gallery cards:")
    for i, card in enumerate(sample_cards, 1):
        name = card.get('name', 'N/A')
        artist = card.get('artist', 'Unknown')
        rarity = card.get('rarity', 'N/A')
        art_url = card.get('imageUris', {}).get('art_crop')
        
        print(f"{i:2}. {name} ({rarity})")
        print(f"     Artist: {artist}")
        print(f"     Art URL: {'✅ Available' if art_url else '❌ Missing'}")
        print()
    
    print(f"🌐 Gallery URL: http://localhost:8000/gallery/")

if __name__ == '__main__':
    main()
