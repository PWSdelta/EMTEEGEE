#!/usr/bin/env python3
"""
Check actual field structure in cards database.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    print("🔍 Checking Card Field Structure")
    print("=" * 50)
    
    cards_collection = get_cards_collection()
    
    # Get one sample card to see field structure
    sample_card = cards_collection.find_one()
    
    if sample_card:
        print("📋 Available fields in cards:")
        for key in sorted(sample_card.keys()):
            print(f"  - {key}")
        
        print(f"\n🖼️ imageUris structure:")
        image_uris = sample_card.get('imageUris', {})
        for key, value in image_uris.items():
            print(f"  - {key}: {value}")
        
        print(f"\n📊 Sample card data:")
        print(f"  Name: {sample_card.get('name')}")
        print(f"  Type: {sample_card.get('type')}")
        print(f"  Rarity: {sample_card.get('rarity')}")
        print(f"  Artist: {sample_card.get('artist')}")
        print(f"  imageStatus: {sample_card.get('imageStatus')}")
        print(f"  highresImage: {sample_card.get('highresImage')}")
        
        # Test the basic query
        basic_query = {'imageUris.art_crop': {'$exists': True, '$ne': None}}
        basic_count = cards_collection.count_documents(basic_query)
        print(f"\n🎨 Cards with art_crop: {basic_count:,}")
        
        # Test with highres filter
        highres_query = {
            'imageUris.art_crop': {'$exists': True, '$ne': None},
            'imageStatus': 'highres_scan'
        }
        highres_count = cards_collection.count_documents(highres_query)
        print(f"📸 High-res art cards: {highres_count:,}")
    
    print(f"\n✨ Field check complete!")

if __name__ == '__main__':
    main()
