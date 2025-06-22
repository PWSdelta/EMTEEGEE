#!/usr/bin/env python3
"""
Test script to verify card self-reference filtering in analyze_markdown.
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.templatetags.card_filters import analyze_markdown

def test_self_reference_filtering():
    """Test that self-references are filtered out properly."""
    
    # Test card data (simulating MongoDB dict)
    test_card = {
        'name': 'Lightning Bolt',
        'uuid': 'test-uuid-123'
    }
    
    # Test content with self-reference
    test_content = """
    This card works well with [[Lightning Bolt]] and [[Shock]].
    You can also use [[lightning bolt]] (case insensitive) in combos.
    Other cards like [[Counterspell]] are also good.
    """
    
    print("Testing self-reference filtering...")
    print(f"Card name: {test_card['name']}")
    print(f"Original content: {test_content}")
    
    # Process with current card context
    result = analyze_markdown(test_content, test_card)
    
    print(f"Processed result: {result}")
    
    # Check that self-references are bold but not linked
    if '<strong>Lightning Bolt</strong>' in result and 'href=' not in result.split('<strong>Lightning Bolt</strong>')[0].split('<strong>Lightning Bolt</strong>')[0]:
        print("✅ Self-reference filtering working correctly!")
    else:
        print("❌ Self-reference filtering may not be working")
    
    # Check that other cards are still linked
    if 'Shock' in result and 'href=' in result:
        print("✅ Other card linking still working!")
    else:
        print("❌ Other card linking may be broken")

if __name__ == "__main__":
    test_self_reference_filtering()
