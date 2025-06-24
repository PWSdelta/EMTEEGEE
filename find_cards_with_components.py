#!/usr/bin/env python3
"""
Find cards with the most analysis components for testing the improved card detail page.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def find_cards_with_components():
    cards = get_cards_collection()
    
    print("🔍 Finding cards with analysis components...")
    
    # First, let's search for Sol Ring specifically
    print("\n🎯 Searching for Sol Ring...")
    sol_ring = cards.find_one({'name': 'Sol Ring'})
    if sol_ring:
        uuid = sol_ring.get('uuid', '')
        components = sol_ring.get('analysis_components', {})
        component_count = len(components) if isinstance(components, dict) else 0
        print(f"✅ Sol Ring found!")
        print(f"   UUID: {uuid}")
        print(f"   Components: {component_count}")
        print(f"   URL: /card/{uuid}/")
        if isinstance(components, dict) and components:
            print(f"   Component types: {', '.join(list(components.keys())[:3])}...")
    else:
        print("❌ Sol Ring not found in database")
    
    # Find cards with analysis_components
    print("\n📊 Finding cards with most components...")
    
    # Get all cards with analysis_components
    cards_with_components = list(cards.find({
        'analysis_components': {'$exists': True, '$ne': {}}
    }).limit(100))
    
    # Sort by component count
    component_counts = []
    for card in cards_with_components:
        components = card.get('analysis_components', {})
        if isinstance(components, dict):
            count = len(components)
            if count > 0:
                component_counts.append({
                    'name': card.get('name', 'Unknown'),
                    'uuid': card.get('uuid', ''),
                    'count': count,
                    'components': list(components.keys())
                })
    
    # Sort by count (descending)
    component_counts.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"Found {len(component_counts)} cards with analysis components")
    
    # Show top 10
    print("\n🏆 Top cards with most components:")
    for i, card_info in enumerate(component_counts[:10], 1):
        name = card_info['name']
        uuid = card_info['uuid']
        count = card_info['count']
        components = card_info['components']
        
        print(f"\n{i}. {name}")
        print(f"   Components: {count}")
        print(f"   UUID: {uuid}")
        print(f"   URL: /card/{uuid}/")
        print(f"   Types: {', '.join(components[:5])}{'...' if len(components) > 5 else ''}")
        
        # Show sample content for the first component
        full_card = cards.find_one({'uuid': uuid})
        if full_card and isinstance(full_card.get('analysis_components'), dict):
            first_comp_key = components[0]
            first_comp = full_card['analysis_components'].get(first_comp_key, {})
            if isinstance(first_comp, dict) and 'content' in first_comp:
                content_preview = first_comp['content'][:100] + "..." if len(first_comp['content']) > 100 else first_comp['content']
                print(f"   Sample ({first_comp_key}): {content_preview}")

if __name__ == "__main__":
    find_cards_with_components()
