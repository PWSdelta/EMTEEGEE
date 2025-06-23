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

from django.http import JsonResponse
from cards.models import get_cards_collection

def test_gallery_logic():
    """Test the exact art gallery logic and return results."""
    print("🔍 Testing Art Gallery Logic")
    print("=" * 40)
    
    try:
        cards_collection = get_cards_collection()
        
        # Replicate the exact logic from the view
        analyzed_cards_cursor = cards_collection.find({
            'analysis.analysis_completed_at': {'$exists': True, '$ne': None},
            'analysis.component_count': 20
        }, {
            'uuid': 1,
            'name': 1,
            'imageUris': 1,
            'artist': 1,
            'setCode': 1,
            'setName': 1,
            'rarity': 1,
            'type': 1,
            'manaCost': 1,
            'colors': 1,
            'scryfallUri': 1,
            'edhrecRank': 1,
            'imageStatus': 1,
            'analysis': 1,
            'releasedAt': 1
        })
        
        # Filter for cards that have art_crop images in Python
        analyzed_cards = []
        for card in analyzed_cards_cursor:
            if card.get('imageUris', {}).get('art_crop'):
                card['is_analyzed'] = True
                card['detail_url'] = f"/card/{card['uuid']}/"
                card['art_url'] = card['imageUris']['art_crop']
                analyzed_cards.append(card)

        print(f"✅ Analyzed cards with art: {len(analyzed_cards)}")
        
        gallery_cards = analyzed_cards.copy()
        
        # If we need more cards to reach 100, add high-quality non-analyzed cards
        remaining_needed = 100 - len(analyzed_cards)
        print(f"📊 Remaining needed: {remaining_needed}")
        
        if remaining_needed > 0:
            # Query for additional high-quality cards (excluding already selected)
            analyzed_uuids = [card['uuid'] for card in analyzed_cards]
            additional_cursor = cards_collection.find({
                'uuid': {'$nin': analyzed_uuids},
                '$or': [
                    {'imageStatus': 'highres_scan'},
                    {'rarity': {'$in': ['mythic', 'rare']}},
                    {'type': {'$regex': 'Planeswalker', '$options': 'i'}},
                    {'edhrecRank': {'$lte': 2000}},
                    {'$and': [
                        {'type': {'$regex': 'Legendary', '$options': 'i'}},
                        {'type': {'$regex': 'Creature', '$options': 'i'}}
                    ]}
                ]
            }, {
                'uuid': 1,
                'name': 1,
                'imageUris': 1,
                'artist': 1,
                'setCode': 1,
                'setName': 1,
                'rarity': 1,
                'type': 1,
                'manaCost': 1,
                'colors': 1,
                'scryfallUri': 1,
                'edhrecRank': 1,
                'imageStatus': 1,
                'releasedAt': 1
            }).limit(remaining_needed + 20)
            
            # Filter for cards that have art_crop images in Python
            additional_cards = []
            for card in additional_cursor:
                if card.get('imageUris', {}).get('art_crop'):
                    card['is_analyzed'] = False
                    card['detail_url'] = f"/card/{card['uuid']}/"
                    card['art_url'] = card['imageUris']['art_crop']
                    additional_cards.append(card)
                    if len(additional_cards) >= remaining_needed:
                        break
            
            print(f"✅ Additional cards found: {len(additional_cards)}")
            
            # Add the additional cards to the gallery
            gallery_cards.extend(additional_cards)
        
        print(f"🎨 Total gallery cards: {len(gallery_cards)}")
        
        # Shuffle the final list
        import random
        random.shuffle(gallery_cards)
        
        context = {
            'gallery_cards': gallery_cards,
            'total_cards': len(gallery_cards),
            'analyzed_count': len(analyzed_cards),
            'page_title': 'MTG Art Gallery'
        }
        
        print(f"📋 Context summary:")
        print(f"   • gallery_cards: {len(context['gallery_cards'])}")
        print(f"   • total_cards: {context['total_cards']}")
        print(f"   • analyzed_count: {context['analyzed_count']}")
        
        # Show first few cards
        if gallery_cards:
            print(f"\n🖼️ First 3 cards:")
            for i, card in enumerate(gallery_cards[:3], 1):
                print(f"   {i}. {card.get('name', 'Unknown')} ({'Analyzed' if card.get('is_analyzed') else 'Not analyzed'})")
        
        return context
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_gallery_logic()
