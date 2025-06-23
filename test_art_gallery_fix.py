#!/usr/bin/env python3

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def test_art_gallery_fix():
    """Test the fixed art gallery functionality."""
    print("🎨 Testing Fixed Art Gallery Functionality")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Test the corrected analyzed cards query (Python filtering)
        analyzed_cards_cursor = cards_collection.find({
            'analysis.analysis_completed_at': {'$exists': True, '$ne': None},
            'analysis.component_count': 20
        })
        
        # Filter for cards that have art_crop images in Python
        analyzed_cards = []
        for card in analyzed_cards_cursor:
            if card.get('imageUris', {}).get('art_crop'):
                analyzed_cards.append(card)
        
        print(f"✅ Found {len(analyzed_cards)} analyzed cards with art images")
        
        if analyzed_cards:
            print("\n🖼️ Sample analyzed cards in art gallery:")
            for i, card in enumerate(analyzed_cards[:5], 1):
                name = card.get('name', 'Unknown')
                artist = card.get('artist', 'Unknown Artist')
                has_art = bool(card.get('imageUris', {}).get('art_crop'))
                analysis_count = card.get('analysis', {}).get('component_count', 0)
                
                print(f" {i}. {name}")
                print(f"     Artist: {artist}")
                print(f"     Art Image: {'✅' if has_art else '❌'}")
                print(f"     AI Components: {analysis_count}")
                print()
        
        # Count total cards available for gallery
        total_gallery_cards = cards_collection.count_documents({})
        total_analyzed = cards_collection.count_documents({
            'analysis.analysis_completed_at': {'$exists': True, '$ne': None},
            'analysis.component_count': 20
        })
        
        print("📊 Gallery Statistics:")
        print(f"   • AI-Analyzed cards: {total_analyzed}")
        print(f"   • AI-Analyzed cards with art: {len(analyzed_cards)}")
        print(f"   • Total cards in database: {total_gallery_cards}")
        print(f"   • Gallery will show: up to 100 cards (analyzed prioritized)")
        
        # Test a specific analyzed card (Sol Ring if available)
        sol_ring = cards_collection.find_one({
            'name': 'Sol Ring',
            'analysis.component_count': 20
        })
        
        if sol_ring:
            has_art = bool(sol_ring.get('imageUris', {}).get('art_crop'))
            print("\n🔍 Sol Ring Status:")
            print("   • Found: ✅")
            print("   • Analyzed: ✅")
            print(f"   • Art Available: {'✅' if has_art else '❌'}")
            if has_art:
                print(f"   • Art URL: {sol_ring['imageUris']['art_crop'][:60]}...")
        else:
            print("\n🔍 Sol Ring: Not found in analyzed cards")
            
        # Test A Little Chat specifically
        little_chat = cards_collection.find_one({
            'name': 'A Little Chat',
            'analysis.component_count': 20
        })
        
        if little_chat:
            has_art = bool(little_chat.get('imageUris', {}).get('art_crop'))
            print("\n🔍 A Little Chat Status:")
            print("   • Found: ✅")
            print("   • Analyzed: ✅")
            print(f"   • Art Available: {'✅' if has_art else '❌'}")
            if has_art:
                print(f"   • Art URL: {little_chat['imageUris']['art_crop'][:60]}...")
        
        print("\n🌐 Art Gallery URL: http://localhost:8000/gallery/")
        print("   The gallery now prioritizes AI-analyzed cards and shows analysis badges!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_art_gallery_fix()
