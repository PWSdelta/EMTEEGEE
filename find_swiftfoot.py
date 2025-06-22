#!/usr/bin/env python3
"""Find and check Swiftfoot Boots card."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    cards_collection = get_cards_collection()
    
    # Find Swiftfoot Boots
    card = cards_collection.find_one({'name': {'$regex': 'Swiftfoot Boots', '$options': 'i'}})
    
    if card:
        print(f"Found: {card.get('name')} - UUID: {card.get('uuid')}")
        
        # Check analysis components
        components = card.get('analysis', {}).get('components', {})
        completed = [k for k, v in components.items() if v]
        print(f"Components completed: {len(completed)}")
        
        if 'combo_suggestions' in components and components['combo_suggestions']:
            print("\n🎯 Has combo_suggestions component!")
            combo_text = components['combo_suggestions']
            print(f"Text length: {len(combo_text)} characters")
            
            # Show first 200 characters
            preview = combo_text[:200] + "..." if len(combo_text) > 200 else combo_text
            print(f"Preview: {preview}")
            
            return card.get('uuid')
        else:
            print("❌ No combo_suggestions component found")
    else:
        print("❌ Swiftfoot Boots not found")
    
    return None

if __name__ == '__main__':
    uuid = main()
    if uuid:
        print(f"\n🌐 Card detail URL: http://localhost:8000/card/{uuid}/")
