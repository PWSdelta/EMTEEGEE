#!/usr/bin/env python3

import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

# Set up logging to see errors
logging.basicConfig(level=logging.DEBUG)

def test_art_gallery_exceptions():
    print("=== TESTING ART GALLERY FOR EXCEPTIONS ===")
    
    from cards.views import art_gallery
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    try:
        print("Calling art_gallery view...")
        response = art_gallery(request)
        print(f"Response status: {response.status_code}")
        
        # Check response content for error messages
        content = response.content.decode('utf-8')
        if 'Error:' in content:
            print("❌ Error found in response content")
            # Find the error line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Error:' in line:
                    print(f"Error line {i}: {line.strip()}")
        else:
            print("✅ No error messages in response content")
            
        # Check if the template context was passed
        if 'Gallery is currently empty' in content:
            print("❌ Gallery is showing as empty - context likely not passed")
        else:
            print("✅ Gallery is not showing as empty")
            
    except Exception as e:
        print(f"❌ Exception occurred in art_gallery view: {e}")
        import traceback
        traceback.print_exc()
    
    # Let's also test the individual components
    print("\n=== TESTING INDIVIDUAL COMPONENTS ===")
    
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        print("✅ Cards collection obtained successfully")
        
        # Test the query
        analyzed_cards_cursor = cards_collection.find({
            'analysis.analysis_completed_at': {'$exists': True, '$ne': None},
            'analysis.component_count': 20
        })
        
        count = 0
        for card in analyzed_cards_cursor:
            count += 1
            if count >= 5:  # Just test first 5
                break
                
        print(f"✅ Found {count} cards in cursor")
        
        # Test the filtering
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
        
        analyzed_cards = []
        for card in analyzed_cards_cursor:
            if card.get('imageUris', {}).get('art_crop'):
                # Convert MongoDB document to plain dict for Django templates
                card_dict = {
                    'uuid': card['uuid'],
                    'name': card['name'],
                    'artist': card.get('artist', 'Unknown Artist'),
                    'setCode': card.get('setCode', ''),
                    'setName': card.get('setName', ''),
                    'rarity': card.get('rarity', ''),
                    'type': card.get('type', ''),
                    'manaCost': card.get('manaCost', ''),
                    'colors': card.get('colors', []),
                    'scryfallUri': card.get('scryfallUri', ''),
                    'edhrecRank': card.get('edhrecRank', None),
                    'imageStatus': card.get('imageStatus', ''),
                    'releasedAt': card.get('releasedAt', ''),
                    'is_analyzed': True,
                    'detail_url': f"/card/{card['uuid']}/",
                    'art_url': card['imageUris']['art_crop'],
                    'imageUris': {
                        'art_crop': card['imageUris']['art_crop'],
                        'large': card['imageUris'].get('large', ''),
                        'normal': card['imageUris'].get('normal', ''),
                        'small': card['imageUris'].get('small', ''),
                    }
                }
                analyzed_cards.append(card_dict)
                
        print(f"✅ Successfully processed {len(analyzed_cards)} analyzed cards")
        
        if analyzed_cards:
            print(f"First card: {analyzed_cards[0]['name']}")
            print(f"First card has art_url: {'art_url' in analyzed_cards[0]}")
        
    except Exception as e:
        print(f"❌ Exception in component testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_art_gallery_exceptions()
