#!/usr/bin/env python3
"""Quick test to verify the Abyss template structure."""

import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.template.loader import render_to_string
from cards.models import get_cards_collection

def test_template_structure():
    """Test that the template has the right structure for grid layout."""
    print("🎨 Testing Abyss Template Structure")
    print("=" * 50)
    
    cards_collection = get_cards_collection()
    
    # Get a few sample cards
    sample_cards = list(cards_collection.find({}).limit(3))
    
    context = {
        'cards': sample_cards,
        'search_query': 'test',
        'total_cards': len(sample_cards),
        'page': 1,
        'total_pages': 1,
        'has_previous': False,
        'has_next': False,
        'is_search': True
    }
    
    try:
        rendered = render_to_string('cards/the_abyss.html', context)
        
        # Check for key CSS classes
        checks = [
            ('abyss-cards-grid', 'Cards grid container'),
            ('abyss-card', 'Individual card'),
            ('abyss-card-image', 'Card image'),
            ('abyss-card-info', 'Card info'),
            ('abyss-card-name', 'Card name'),
            ('abyss-search-hero', 'Search hero section')
        ]
        
        for css_class, description in checks:
            found = css_class in rendered
            status = "✅" if found else "❌"
            print(f"{status} {description}: {css_class}")
        
        print(f"\n📊 Template rendered successfully: {len(rendered)} characters")
        print(f"🃏 Cards in template: {len(sample_cards)}")
        
    except Exception as e:
        print(f"❌ Template error: {e}")

if __name__ == '__main__':
    test_template_structure()
