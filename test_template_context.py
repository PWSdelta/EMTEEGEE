#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.views import art_gallery
from django.test import RequestFactory
from django.template.loader import render_to_string

def test_template_context():
    print("=== TESTING ART GALLERY TEMPLATE CONTEXT ===")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    # Call the art_gallery view
    response = art_gallery(request)
    print(f"Response status: {response.status_code}")
    print(f"Response type: {type(response)}")
    
    # Check if it's a TemplateResponse
    if hasattr(response, 'context_data'):
        context = response.context_data
        print(f"Context keys: {list(context.keys())}")
        
        if 'gallery_cards' in context:
            gallery_cards = context['gallery_cards']
            print(f"Gallery cards count: {len(gallery_cards)}")
            
            if gallery_cards:
                print(f"First card: {gallery_cards[0].get('name', 'No name')}")
                print(f"First card has art_url: {'art_url' in gallery_cards[0]}")
                print(f"First card art_url: {gallery_cards[0].get('art_url', 'No art_url')}")
            else:
                print("Gallery cards list is empty!")
        else:
            print("No gallery_cards in context!")
    else:
        # For HttpResponse, we need to check differently
        print("This is an HttpResponse, not TemplateResponse")
        
        # Let's manually call the context logic
        try:
            from cards.models import get_cards_collection
            
            cards_collection = get_cards_collection()
            
            # Test the analyzed cards query
            analyzed_cards_cursor = cards_collection.find({
                'analysis.analysis_completed_at': {'$exists': True, '$ne': None},
                'analysis.component_count': 20
            })
            
            analyzed_cards = []
            for card in analyzed_cards_cursor:
                if card.get('imageUris', {}).get('art_crop'):
                    card['is_analyzed'] = True
                    card['detail_url'] = f"/card/{card['uuid']}/"
                    card['art_url'] = card['imageUris']['art_crop']
                    analyzed_cards.append(card)
            
            print(f"Manual query found {len(analyzed_cards)} analyzed cards with art_crop")
            
            if analyzed_cards:
                print(f"First analyzed card: {analyzed_cards[0].get('name')}")
                print(f"First analyzed card art_url: {analyzed_cards[0].get('art_url')}")
            
            # Test template rendering manually
            context = {
                'gallery_cards': analyzed_cards[:10],  # Just test with first 10
                'total_cards': len(analyzed_cards),
                'analyzed_count': len(analyzed_cards),
                'page_title': 'MTG Art Gallery - Debug'
            }
            
            print(f"\nTesting template with context:")
            print(f"- gallery_cards: {len(context['gallery_cards'])} cards")
            print(f"- total_cards: {context['total_cards']}")
            
            # Try to render the template
            try:
                rendered = render_to_string('cards/art_gallery.html', context)
                print(f"Template rendered successfully, length: {len(rendered)}")
                
                # Check if it contains the expected content
                if 'Gallery is currently empty' in rendered:
                    print("❌ Template still shows 'Gallery is currently empty'")
                elif 'card-slide' in rendered:
                    print("✅ Template contains card slides")
                elif context['gallery_cards']:
                    print("⚠️  Template rendered but no card slides found")
                    # Print a snippet to see what's happening
                    lines = rendered.split('\n')
                    for i, line in enumerate(lines):
                        if 'gallery-container' in line or 'swiper-wrapper' in line or 'card-slide' in line:
                            print(f"Line {i}: {line.strip()}")
                
            except Exception as e:
                print(f"❌ Template rendering failed: {e}")
                
        except Exception as e:
            print(f"Manual context testing failed: {e}")

if __name__ == "__main__":
    test_template_context()
