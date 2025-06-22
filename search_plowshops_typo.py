#!/usr/bin/env python3
"""Search for Plowshops typo across all cards."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def search_plowshops_typo():
    """Search for the Plowshops typo across all cards."""
    print("🔍 Searching for 'Plowshops' Typo Across All Cards")
    print("=" * 60)
    
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        
        # Search for any mention of "Plowshops" in analysis components
        cards_with_typo = list(cards_collection.find({
            'analysis.components': {
                '$regex': 'Plowshops',
                '$options': 'i'  # Case insensitive
            }
        }))
        
        print(f"🔍 Found {len(cards_with_typo)} cards with 'Plowshops' typo")
        
        if not cards_with_typo:
            print("✅ No cards found with 'Plowshops' typo!")
            
            # Let's also search for any variations
            print("\n🔍 Searching for other potential typos...")
            
            variations = ['Plowshares', 'Swords to', 'Plow']
            for variation in variations:
                count = cards_collection.count_documents({
                    'analysis.components': {
                        '$regex': variation,
                        '$options': 'i'
                    }
                })
                print(f"   Cards mentioning '{variation}': {count}")
            
            return
        
        # Show details of cards with the typo
        for card in cards_with_typo:
            print(f"\n🃏 Card: {card.get('name', 'Unknown')}")
            print(f"   UUID: {card.get('uuid', 'Unknown')}")
            
            components = card.get('analysis', {}).get('components', {})
            
            for component_name, component_text in components.items():
                if component_text and 'Plowshops' in component_text:
                    print(f"   📝 Component: {component_name}")
                    
                    # Show the lines with the typo
                    lines = component_text.split('\n')
                    for i, line in enumerate(lines):
                        if 'Plowshops' in line:
                            print(f"      Line {i+1}: {line.strip()}")
                    
                    # Offer to fix it
                    print(f"      🔧 Ready to fix: {component_name}")
        
        # Ask if we should fix them
        print(f"\n🛠️ Found typos in {len(cards_with_typo)} cards. Fixing them...")
        
        total_fixes = 0
        for card in cards_with_typo:
            card_fixes = 0
            components = card.get('analysis', {}).get('components', {})
            
            for component_name, component_text in components.items():
                if component_text and 'Plowshops' in component_text:
                    # Fix the typo
                    fixed_text = component_text.replace('[[Swords to Plowshops]]', '[[Swords to Plowshares]]')
                    fixed_text = fixed_text.replace('Swords to Plowshops', 'Swords to Plowshares')
                    fixed_text = fixed_text.replace('Plowshops', 'Plowshares')
                    
                    # Update in database
                    result = cards_collection.update_one(
                        {'uuid': card['uuid']},
                        {'$set': {f'analysis.components.{component_name}': fixed_text}}
                    )
                    
                    if result.modified_count > 0:
                        print(f"✅ Fixed typo in {card.get('name')} - {component_name}")
                        card_fixes += 1
                        total_fixes += 1
                    else:
                        print(f"❌ Failed to fix typo in {card.get('name')} - {component_name}")
            
            if card_fixes > 0:
                print(f"   📊 Made {card_fixes} fixes for {card.get('name')}")
        
        print(f"\n🎉 Total fixes made: {total_fixes}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_plowshops_typo()
