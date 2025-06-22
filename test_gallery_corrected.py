#!/usr/bin/env python3
"""
Test the corrected art gallery query.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    print("🎨 Testing Corrected Art Gallery Query")
    print("=" * 50)
    
    cards_collection = get_cards_collection()
    
    # Test the corrected query
    query = {'imageUris.art_crop': {'$exists': True, '$ne': None}}
    count = cards_collection.count_documents(query)
    print(f"Cards with art_crop: {count:,}")
    
    if count > 0:
        # Get a sample
        sample = cards_collection.find_one(query, {
            'name': 1, 
            'imageUris.art_crop': 1, 
            'artist': 1,
            'rarity': 1,
            'uuid': 1
        })
        
        if sample:
            print(f"\nSample card: {sample.get('name')}")
            print(f"Artist: {sample.get('artist', 'Unknown')}")
            print(f"Rarity: {sample.get('rarity', 'Unknown')}")
            print(f"UUID: {sample.get('uuid')}")
            art_url = sample.get('imageUris', {}).get('art_crop', 'N/A')
            print(f"Art URL: {art_url}")
        
        # Test gallery query
        print(f"\nTesting full gallery query...")
        gallery_query = {
            'imageUris.art_crop': {'$exists': True, '$ne': None},
            '$or': [
                {'imageStatus': 'highres_scan'},
                {'rarity': {'$in': ['mythic', 'rare']}},
                {'type_line': {'$regex': 'Planeswalker', '$options': 'i'}},
                {'edhrecRank': {'$lte': 2000}},
                {'$and': [
                    {'type_line': {'$regex': 'Legendary', '$options': 'i'}},
                    {'type_line': {'$regex': 'Creature', '$options': 'i'}}
                ]}
            ]
        }
        
        gallery_count = cards_collection.count_documents(gallery_query)
        print(f"Gallery query matches: {gallery_count:,}")
        
        # Get top 5 for testing
        gallery_samples = list(cards_collection.find(gallery_query, {
            'name': 1, 'artist': 1, 'rarity': 1, 'imageUris.art_crop': 1
        }).limit(5))
        
        print(f"\nSample gallery cards:")
        for i, card in enumerate(gallery_samples, 1):
            name = card.get('name', 'Unknown')
            artist = card.get('artist', 'Unknown')
            rarity = card.get('rarity', 'Unknown')
            print(f"{i}. {name} ({rarity}) by {artist}")
        
        print(f"\n✅ Art gallery should be working!")
        print(f"URL: http://localhost:8000/gallery/")
    
    else:
        print("❌ No cards found with art_crop images")

if __name__ == '__main__':
    main()
