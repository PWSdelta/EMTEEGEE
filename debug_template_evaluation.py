#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.template import Context, Template

def debug_template_evaluation():
    print("=== DEBUGGING TEMPLATE EVALUATION ===")
    
    # Create test data that matches our expected structure
    test_cards = [
        {
            'uuid': 'test-uuid-1',
            'name': 'Test Card 1',
            'art_url': 'https://example.com/art1.jpg',
            'artist': 'Test Artist 1',
            'is_analyzed': True,
            'detail_url': '/card/test-uuid-1/',
            'imageUris': {
                'art_crop': 'https://example.com/art1.jpg'
            }
        },
        {
            'uuid': 'test-uuid-2', 
            'name': 'Test Card 2',
            'art_url': 'https://example.com/art2.jpg',
            'artist': 'Test Artist 2',
            'is_analyzed': False,
            'detail_url': '/card/test-uuid-2/',
            'imageUris': {
                'art_crop': 'https://example.com/art2.jpg'  
            }
        }
    ]
    
    context_data = {
        'gallery_cards': test_cards,
        'total_cards': len(test_cards),
        'analyzed_count': 1,
        'page_title': 'MTG Art Gallery - Debug'
    }
    
    # Test the template condition directly
    template_str = """
    {% if gallery_cards %}
        <p>GALLERY CARDS EXIST: {{ gallery_cards|length }} cards</p>
        {% for card in gallery_cards %}
            <p>Card {{ forloop.counter }}: {{ card.name }}</p>
        {% endfor %}
    {% else %}
        <p>NO GALLERY CARDS FOUND</p>
    {% endif %}
    
    <hr>
    <p>Gallery cards variable: {{ gallery_cards }}</p>
    <p>Gallery cards length: {{ gallery_cards|length }}</p>
    <p>Gallery cards type: {{ gallery_cards|default:"NULL" }}</p>
    """
    
    template = Template(template_str)
    context = Context(context_data)
    rendered = template.render(context)
    
    print("Template evaluation result:")
    print(rendered)
    print()
    
    # Now test with the actual view response
    print("=== TESTING ACTUAL VIEW RESPONSE ===")
    from cards.views import art_gallery
    from django.test import RequestFactory
    import json
    
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    response = art_gallery(request)
    
    # Since it's an HttpResponse, let's look at the content
    content = response.content.decode('utf-8')
    
    # Check for key indicators
    if 'Gallery is currently empty' in content:
        print("❌ Response contains 'Gallery is currently empty'")
    else:
        print("✅ Response does NOT contain 'Gallery is currently empty'")
        
    if 'carousel-item' in content:
        print("✅ Response contains carousel items")
    else:
        print("❌ Response does NOT contain carousel items")
        
    if 'AI-Analyzed Cards' in content:
        print("✅ Response contains analysis stats")
    else:
        print("❌ Response does NOT contain analysis stats")
    
    # Count carousel items
    carousel_count = content.count('carousel-item')
    print(f"Carousel items found: {carousel_count}")
    
    # Let's also directly inspect what the view function is doing
    print("\n=== DEBUGGING VIEW FUNCTION DIRECTLY ===")
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        
        # Get the same data the view would get
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
                card['is_analyzed'] = True
                card['detail_url'] = f"/card/{card['uuid']}/"
                card['art_url'] = card['imageUris']['art_crop']
                analyzed_cards.append(card)
        
        print(f"Analyzed cards found: {len(analyzed_cards)}")
        
        if analyzed_cards:
            first_card = analyzed_cards[0]
            print(f"First card name: {first_card.get('name')}")
            print(f"First card UUID: {first_card.get('uuid')}")
            print(f"First card has art_url: {'art_url' in first_card}")
            print(f"First card art_url value: {first_card.get('art_url', 'NO ART URL')}")
            
            # Test the template with actual data
            print("\n=== TESTING TEMPLATE WITH REAL DATA ===")
            context_real = {
                'gallery_cards': analyzed_cards[:5],  # Just test with first 5
                'total_cards': len(analyzed_cards),
                'analyzed_count': len(analyzed_cards),
                'page_title': 'MTG Art Gallery'
            }
            
            template_real = Template(template_str)
            context_real_obj = Context(context_real)
            rendered_real = template_real.render(context_real_obj)
            
            print("Real data template result:")
            print(rendered_real)
        
    except Exception as e:
        print(f"Error in direct view debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_template_evaluation()
