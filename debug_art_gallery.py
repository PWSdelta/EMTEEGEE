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

def debug_art_gallery():
    """Debug the art gallery view logic."""
    print("🔍 Debugging Art Gallery View")
    print("=" * 40)
    
    try:
        cards_collection = get_cards_collection()
        
        # Test the exact query from the view
        print("Step 1: Testing analyzed cards query...")
        analyzed_cards_cursor = cards_collection.find({
            'analysis.analysis_completed_at': {'$exists': True, '$ne': None},
            'analysis.component_count': 20
        })
        
        analyzed_with_art = []
        total_analyzed = 0
        
        for card in analyzed_cards_cursor:
            total_analyzed += 1
            if card.get('imageUris', {}).get('art_crop'):
                analyzed_with_art.append(card)
                
        print(f"   • Total analyzed cards found: {total_analyzed}")
        print(f"   • Analyzed cards with art: {len(analyzed_with_art)}")
        
        if analyzed_with_art:
            print("\nStep 2: Sample analyzed cards with art:")
            for i, card in enumerate(analyzed_with_art[:3], 1):
                name = card.get('name', 'Unknown')
                art_url = card.get('imageUris', {}).get('art_crop', '')
                print(f"   {i}. {name}")
                print(f"      Art URL: {art_url[:50]}...")
        
        # Test fallback query for non-analyzed cards
        print("\nStep 3: Testing fallback query...")
        analyzed_uuids = [card['uuid'] for card in analyzed_with_art]
        
        fallback_cursor = cards_collection.find({
            'uuid': {'$nin': analyzed_uuids},
            'rarity': {'$in': ['mythic', 'rare']}
        }).limit(10)
        
        fallback_with_art = []
        for card in fallback_cursor:
            if card.get('imageUris', {}).get('art_crop'):
                fallback_with_art.append(card)
                
        print(f"   • Fallback cards with art: {len(fallback_with_art)}")
        
        # Total gallery cards
        total_gallery = len(analyzed_with_art) + len(fallback_with_art)
        print(f"\nStep 4: Total gallery cards: {total_gallery}")
        
        if total_gallery == 0:
            print("\n❌ ISSUE FOUND: No cards have art_crop images!")
            
            # Check if any cards have imageUris at all
            cards_with_images = cards_collection.count_documents({
                'imageUris': {'$exists': True, '$ne': None}
            })
            print(f"   • Cards with imageUris field: {cards_with_images}")
            
            # Check a sample card's imageUris structure
            sample_card = cards_collection.find_one({'imageUris': {'$exists': True}})
            if sample_card:
                image_keys = list(sample_card.get('imageUris', {}).keys())
                print(f"   • Sample imageUris keys: {image_keys}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_art_gallery()
