#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.shortcuts import render
from django.template import Context, Template
from cards.models import get_cards_collection

def test_direct_context():
    print("=== DIRECT CONTEXT TEST ===")
    
    # Get cards directly like the view does
    cards_collection = get_cards_collection()
    
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
    
    # Convert like the updated view does
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
    
    print(f"Found {len(analyzed_cards)} analyzed cards")
    
    # Test context
    context = {
        'gallery_cards': analyzed_cards[:5],  # First 5 for testing
        'total_cards': len(analyzed_cards),
        'analyzed_count': len(analyzed_cards),
        'page_title': 'MTG Art Gallery'
    }
    
    print(f"Context gallery_cards type: {type(context['gallery_cards'])}")
    print(f"Context gallery_cards length: {len(context['gallery_cards'])}")
    if context['gallery_cards']:
        print(f"First card type: {type(context['gallery_cards'][0])}")
        print(f"First card keys: {list(context['gallery_cards'][0].keys())}")
        print(f"First card name: {context['gallery_cards'][0]['name']}")
      # Test template condition directly
    template_str = '''
    {% if gallery_cards %}
    GALLERY_CARDS_TRUE: {{ gallery_cards|length }} cards found
    {% else %}
    GALLERY_CARDS_FALSE: No cards
    {% endif %}
    
    Gallery cards boolean: {{ gallery_cards|yesno:"YES,NO,MAYBE" }}
    Gallery cards length: {{ gallery_cards|length }}
    '''
    
    template = Template(template_str)
    context_obj = Context(context)
    rendered = template.render(context_obj)
    
    print("Template test result:")
    print(rendered)
    
    # Now test what the actual view returns
    print("\n=== TESTING ACTUAL VIEW FUNCTION ===")
    from cards.views import art_gallery
    from django.test import RequestFactory
    from django.http import HttpRequest
    
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    # Monkey patch to see what context is passed
    original_render = render
    captured_context = None
    
    def mock_render(request, template_name, context=None):
        nonlocal captured_context
        captured_context = context
        return original_render(request, template_name, context)
    
    # Temporarily replace render
    import cards.views
    cards.views.render = mock_render
    
    try:
        response = art_gallery(request)
        print(f"Response status: {response.status_code}")
        
        if captured_context:
            print(f"Captured context keys: {list(captured_context.keys())}")
            if 'gallery_cards' in captured_context:
                gallery_cards = captured_context['gallery_cards']
                print(f"Captured gallery_cards type: {type(gallery_cards)}")
                print(f"Captured gallery_cards length: {len(gallery_cards) if gallery_cards else 0}")
                print(f"Captured gallery_cards bool: {bool(gallery_cards)}")
                
                if gallery_cards:
                    print(f"First captured card: {gallery_cards[0]['name']}")
                else:
                    print("Captured gallery_cards is empty or falsy!")
            else:
                print("No gallery_cards in captured context!")
        else:
            print("No context captured!")
            
    finally:
        # Restore original render
        cards.views.render = original_render

if __name__ == "__main__":
    test_direct_context()
