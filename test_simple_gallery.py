#!/usr/bin/env python3
"""
Super simple test for the art gallery to verify it works.
"""
import os
import sys
import django
from django.conf import settings

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.views import art_gallery
from django.test import RequestFactory

def test_simple_gallery():
    """Test the art gallery view directly."""
    print("Testing art gallery view...")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    # Call the view
    response = art_gallery(request)
    
    print(f"Response status: {response.status_code}")
    
    # Check if it's a proper response
    if hasattr(response, 'context_data'):
        context = response.context_data
        print(f"Context keys: {list(context.keys())}")
        
        gallery_cards = context.get('gallery_cards', [])
        print(f"Gallery cards count: {len(gallery_cards)}")
        
        if gallery_cards:
            print(f"First card: {gallery_cards[0]['name']}")
            print(f"First card art URL: {gallery_cards[0]['art_url']}")
            print("✅ Gallery has cards!")
        else:
            print("❌ Gallery is empty")
    else:
        print("No context data available")
    
    return response

if __name__ == "__main__":
    test_simple_gallery()
