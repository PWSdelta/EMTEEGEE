#!/usr/bin/env python3
"""Test the art gallery view directly to see what data is passed to template."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.test import RequestFactory
from cards.views import art_gallery

def main():
    print("🎨 Testing Art Gallery View")
    print("=" * 50)
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    # Call the view
    response = art_gallery(request)
    
    print(f"Response status: {response.status_code}")
    
    # Check context data if available
    if hasattr(response, 'context_data'):
        context = response.context_data
        gallery_cards = context.get('gallery_cards', [])
        total_cards = context.get('total_cards', 0)
        
        print(f"Gallery cards in context: {len(gallery_cards)}")
        print(f"Total cards reported: {total_cards}")
        
        if gallery_cards:
            print(f"First few cards:")
            for i, card in enumerate(gallery_cards[:3]):
                print(f"  {i+1}. {card.get('name', 'Unknown')}")
    else:
        print("No context data available (might be rendered template)")
    
    print(f"\n🌐 Gallery URL: http://localhost:8000/gallery/")

if __name__ == '__main__':
    main()
