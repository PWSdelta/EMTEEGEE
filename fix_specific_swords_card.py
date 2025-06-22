#!/usr/bin/env python3
"""Fix typo in Swords to Plowshares card - specific UUID d56255aa-7e1f-4314-be35-dd29f0a52270."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def fix_specific_swords_card():
    """Fix typo in the specific Swords to Plowshares card."""
    print("🔧 Fixing Swords to Plowshares Card Typo")
    print("=" * 50)
    
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        
        # Target the specific card UUID
        target_uuid = "d56255aa-7e1f-4314-be35-dd29f0a52270"
        
        swords_card = cards_collection.find_one({
            'uuid': target_uuid
        })
        
        if not swords_card:
            print(f"❌ Card with UUID {target_uuid} not found")
            return
        
        print(f"✅ Found card: {swords_card.get('name')}")
        print(f"   UUID: {swords_card.get('uuid')}")
        
        # Check analysis components
        analysis = swords_card.get('analysis', {})
        components = analysis.get('components', {})
        
        if not components:
            print("❌ No analysis components found")
            return
        
        print(f"📊 Checking {len(components)} analysis components...")
        
        # Look for typos and show what we find
        fixes_made = 0
        
        for component_name, component_text in components.items():
            if component_text:
                # Check for the specific typo
                if 'Plowshops' in component_text:
                    print(f"\n🔍 FOUND TYPO in component: {component_name}")
                    
                    # Show the problematic text
                    lines = component_text.split('\n')
                    for i, line in enumerate(lines):
                        if 'Plowshops' in line:
                            print(f"   Line {i+1}: {line.strip()}")
                    
                    # Fix the typo
                    fixed_text = component_text.replace('[[Swords to Plowshops]]', '[[Swords to Plowshares]]')
                    fixed_text = fixed_text.replace('Swords to Plowshops', 'Swords to Plowshares')
                    fixed_text = fixed_text.replace('Plowshops', 'Plowshares')  # Catch any standalone instances
                    
                    # Update in database
                    result = cards_collection.update_one(
                        {'uuid': target_uuid},
                        {'$set': {f'analysis.components.{component_name}': fixed_text}}
                    )
                    
                    if result.modified_count > 0:
                        print(f"   ✅ Fixed typo in {component_name}")
                        fixes_made += 1
                    else:
                        print(f"   ❌ Failed to update {component_name}")
                
                # Also check for any references to Swords to Plowshares (correct spelling)
                elif 'Swords to Plowshares' in component_text or 'Plowshares' in component_text:
                    print(f"\n📝 Component '{component_name}' mentions Swords to Plowshares (checking spelling...)")
                    
                    # Show lines that mention it
                    lines = component_text.split('\n')
                    for i, line in enumerate(lines):
                        if 'Plowshares' in line or 'Swords to' in line:
                            print(f"   Line {i+1}: {line.strip()}")
        
        if fixes_made > 0:
            print(f"\n🎉 Successfully fixed {fixes_made} typo(s)!")
        else:
            print(f"\n🔍 No typos found in this card.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_specific_swords_card()
