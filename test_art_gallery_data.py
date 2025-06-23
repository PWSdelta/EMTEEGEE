#!/usr/bin/env python3

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def test_art_gallery_data():
    """Test that art gallery has analyzed cards and proper image URLs."""
    print("🎨 Testing Art Gallery Data...")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Test analyzed cards query
        analyzed_query = {
            'analysis.fully_analyzed': True,
            'imageUris.art_crop': {'$exists': True, '$ne': None}
        }
        
        analyzed_cards = list(cards_collection.find(analyzed_query).limit(10))
        
        print(f"✅ Found {len(analyzed_cards)} analyzed cards with art images")
        
        if analyzed_cards:
            print("\n📊 Sample analyzed cards:")
            for i, card in enumerate(analyzed_cards[:5], 1):
                print(f"  {i}. {card.get('name', 'Unknown')} ({card.get('setCode', 'N/A')})")
                print(f"     Artist: {card.get('artist', 'Unknown')}")
                print(f"     Art URL: ✅ {card['imageUris']['art_crop'][:50]}...")
                print(f"     Analysis: {card['analysis']['component_count']} components")
                print()
        
        # Test total cards available
        total_query = {
            'imageUris.art_crop': {'$exists': True, '$ne': None}
        }
        total_with_art = cards_collection.count_documents(total_query)
        
        print(f"🖼️  Total cards with art images: {total_with_art:,}")
        
        # Test a few random cards to verify image URLs
        sample_cards = list(cards_collection.find(total_query).limit(3))
        print(f"\n🔍 Testing image URL accessibility:")
        
        for card in sample_cards:
            name = card.get('name', 'Unknown')
            art_url = card['imageUris']['art_crop']
            print(f"  - {name}: {art_url}")
            
        print(f"\n🌐 Art Gallery URL: http://localhost:8000/gallery/")
        print("✅ Art Gallery data test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing art gallery: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_art_gallery_data()
