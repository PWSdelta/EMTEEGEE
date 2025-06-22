#!/usr/bin/env python3
"""
Test script for the enhanced card linking system.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection
from cards.templatetags.card_filters import find_card_by_name

def main():
    print("🔍 Testing Enhanced Card Linking System")
    print("=" * 50)
    
    # Get some sample cards from the database
    cards_collection = get_cards_collection()
    sample_cards = list(cards_collection.find({}, {'name': 1, 'uuid': 1}).limit(5))
    
    print(f"\n📋 Found {len(sample_cards)} sample cards:")
    for i, card in enumerate(sample_cards, 1):
        name = card.get('name', 'N/A')
        uuid = card.get('uuid', 'N/A')
        print(f"{i}. {name} - {uuid}")
    
    if sample_cards:
        print(f"\n🧪 Testing card lookup function:")
        test_card = sample_cards[0]
        test_name = test_card.get('name')
        test_uuid = test_card.get('uuid')
        
        # Test exact name lookup
        found_uuid = find_card_by_name(test_name)
        print(f"Looking up '{test_name}':")
        print(f"  Expected UUID: {test_uuid}")
        print(f"  Found UUID:    {found_uuid}")
        print(f"  Match: {'✅' if found_uuid == test_uuid else '❌'}")
        
        # Test partial name lookup
        if len(test_name) > 3:
            partial_name = test_name[:len(test_name)//2]
            found_uuid_partial = find_card_by_name(partial_name)
            print(f"\nPartial lookup '{partial_name}':")
            print(f"  Found UUID: {found_uuid_partial}")
            print(f"  Match: {'✅' if found_uuid_partial == test_uuid else '❌'}")
        
        # Test case insensitive lookup
        case_test = test_name.upper()
        found_uuid_case = find_card_by_name(case_test)
        print(f"\nCase insensitive lookup '{case_test}':")
        print(f"  Found UUID: {found_uuid_case}")
        print(f"  Match: {'✅' if found_uuid_case == test_uuid else '❌'}")
    
    print(f"\n🎯 Testing markdown analysis with card links:")
    from cards.templatetags.card_filters import analyze_markdown
    
    if sample_cards:
        card_name = sample_cards[0].get('name')
        test_markdown = f"""
# Test Analysis

This card works well with [[{card_name}]] and [[Lightning Bolt]].

You might also consider:
- [[Counterspell]]
- [[Brainstorm]]
- [[{card_name}]] (duplicate test)

## Combos
The interaction between [[{card_name}]] and [[Nonexistent Card]] is interesting.
"""
        
        print("Input markdown:")
        print(test_markdown)
        
        print("\nOutput HTML:")
        html_output = analyze_markdown(test_markdown)
        print(html_output)
    
    print(f"\n✨ Card linking system test complete!")

if __name__ == '__main__':
    main()
