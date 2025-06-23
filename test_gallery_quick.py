#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def test_gallery_quick():
    print("=== QUICK GALLERY TEST ===")
    
    try:
        from cards.models import get_cards_collection
        cards_collection = get_cards_collection()
        
        # Test the aggregation pipeline
        pipeline = [
            {'$match': {'imageUris.art_crop': {'$exists': True}}},
            {'$sample': {'size': 5}},  # Just 5 for testing
            {'$project': {
                'uuid': 1,
                'name': 1,
                'imageUris': 1,
                'artist': 1
            }}
        ]
        
        cards_cursor = cards_collection.aggregate(pipeline)
        cards = list(cards_cursor)
        
        print(f"✅ Found {len(cards)} cards with art_crop")
        
        if cards:
            for i, card in enumerate(cards[:3], 1):
                print(f"Card {i}: {card.get('name')} by {card.get('artist', 'Unknown')}")
                print(f"  Art URL: {card.get('imageUris', {}).get('art_crop', 'No URL')}")
                
        # Test the view
        from cards.views import art_gallery
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/gallery/')
        response = art_gallery(request)
        
        content = response.content.decode('utf-8')
        
        if 'Gallery is currently empty' in content:
            print("❌ Gallery shows empty")
        elif 'carousel-item' in content:
            count = content.count('carousel-item')
            print(f"✅ Gallery has {count} carousel items")
        else:
            print("⚠️  Gallery status unclear")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gallery_quick()
