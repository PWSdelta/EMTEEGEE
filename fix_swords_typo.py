#!/usr/bin/env python3
"""Fix typo: [[Swords to Plowshops]] → [[Swords to Plowshares]] across all analysis components."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def fix_swords_typo():
    """Fix the Swords to Plowshares typo across all analysis components."""
    print("🔧 Fixing Swords to Plowshares Typo")
    print("=" * 60)
    
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        
        # Search for cards with the typo in any analysis component
        typo_pattern = "Swords to Plowshops"
        correct_text = "Swords to Plowshares"
        
        # Find all cards with analysis components containing the typo
        cards_with_typo = list(cards_collection.find({
            "$or": [
                {"analysis.components.play_tips": {"$regex": typo_pattern}},
                {"analysis.components.tactical_analysis": {"$regex": typo_pattern}},
                {"analysis.components.synergy_analysis": {"$regex": typo_pattern}},
                {"analysis.components.combo_suggestions": {"$regex": typo_pattern}},
                {"analysis.components.power_level_assessment": {"$regex": typo_pattern}},
                {"analysis.components.competitive_analysis": {"$regex": typo_pattern}},
                {"analysis.components.format_analysis": {"$regex": typo_pattern}},
                {"analysis.components.mulligan_considerations": {"$regex": typo_pattern}},
                {"analysis.components.sideboard_guide": {"$regex": typo_pattern}},
                {"analysis.components.budget_alternatives": {"$regex": typo_pattern}},
                {"analysis.components.deck_archetypes": {"$regex": typo_pattern}},
                {"analysis.components.meta_positioning": {"$regex": typo_pattern}},
                {"analysis.components.investment_outlook": {"$regex": typo_pattern}},
                {"analysis.components.thematic_analysis": {"$regex": typo_pattern}},
                {"analysis.components.historical_context": {"$regex": typo_pattern}},
                {"analysis.components.rules_clarifications": {"$regex": typo_pattern}},
                {"analysis.components.art_flavor_analysis": {"$regex": typo_pattern}},
                {"analysis.components.new_player_guide": {"$regex": typo_pattern}},
                {"analysis.components.advanced_interactions": {"$regex": typo_pattern}},
                {"analysis.components.design_philosophy": {"$regex": typo_pattern}}
            ]
        }))
        
        print(f"🔍 Found {len(cards_with_typo)} cards with the typo")
        
        if not cards_with_typo:
            print("✅ No cards found with the typo - might already be fixed!")
            return
        
        fixed_count = 0
        component_fixes = {}
        
        for card in cards_with_typo:
            card_name = card.get('name', 'Unknown')
            card_uuid = card.get('uuid', 'Unknown')
            
            print(f"\n🃏 Fixing {card_name} ({card_uuid[:8]}...)")
            
            # Check each component for the typo
            components = card.get('analysis', {}).get('components', {})
            card_updated = False
            
            for component_name, component_text in components.items():
                if component_text and typo_pattern in component_text:
                    # Fix the typo
                    fixed_text = component_text.replace(typo_pattern, f"[[{correct_text}]]")
                    
                    # Update in database
                    result = cards_collection.update_one(
                        {"uuid": card_uuid},
                        {"$set": {f"analysis.components.{component_name}": fixed_text}}
                    )
                    
                    if result.modified_count > 0:
                        print(f"   ✅ Fixed in {component_name}")
                        card_updated = True
                        
                        # Track component fixes
                        if component_name not in component_fixes:
                            component_fixes[component_name] = 0
                        component_fixes[component_name] += 1
                    else:
                        print(f"   ❌ Failed to fix in {component_name}")
            
            if card_updated:
                fixed_count += 1
        
        print(f"\n🎉 Fix Summary:")
        print(f"   📊 Cards processed: {len(cards_with_typo)}")
        print(f"   ✅ Cards fixed: {fixed_count}")
        print(f"   🔧 Component fixes:")
        
        for component, count in component_fixes.items():
            print(f"      - {component}: {count} fixes")
        
        print(f"\n✅ All instances of '[[{typo_pattern}]]' have been fixed to '[[{correct_text}]]'!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_swords_typo()
