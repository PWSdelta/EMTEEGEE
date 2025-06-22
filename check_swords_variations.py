#!/usr/bin/env python3
"""Check specific card for Swords to Plowshares variations and fix any typos."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def check_specific_card_swords():
    """Check the specific card for Swords variations."""
    print("🔍 Checking Specific Card for Swords Variations")
    print("=" * 60)
    
    try:
        from cards.models import get_cards_collection
        
        cards_collection = get_cards_collection()
        
        # The specific card UUID from the URL
        card_uuid = "d56255aa-7e1f-4314-be35-dd29f0a52270"
        
        # Get the specific card
        card = cards_collection.find_one({"uuid": card_uuid})
        
        if not card:
            print(f"❌ Card with UUID {card_uuid} not found")
            return
        
        card_name = card.get('name', 'Unknown')
        print(f"🃏 Found card: {card_name}")
        
        # Check all analysis components for any Swords variations
        components = card.get('analysis', {}).get('components', {})
        
        if not components:
            print("❌ No analysis components found for this card")
            return
        
        print(f"📊 Checking {len(components)} analysis components...")
        
        # Search patterns for various typos
        search_patterns = [
            "Swords to Plowshops",
            "Swords to Plowshop", 
            "[[Swords to Plowshops]]",
            "[[Swords to Plowshop]]",
            "Swords to Plowshares",  # Correct version
            "[[Swords to Plowshares]]"  # Correct linked version
        ]
        
        found_patterns = {}
        
        for component_name, component_text in components.items():
            if component_text:
                for pattern in search_patterns:
                    if pattern in component_text:
                        if pattern not in found_patterns:
                            found_patterns[pattern] = []
                        found_patterns[pattern].append(component_name)
        
        if found_patterns:
            print(f"\n🔍 Found Swords variations:")
            for pattern, components_list in found_patterns.items():
                print(f"   '{pattern}' in: {', '.join(components_list)}")
        else:
            print("ℹ️  No 'Swords to Plowshares' variations found in this card")
        
        # Now let's search more broadly in the database
        print(f"\n🔍 Searching entire database for Swords variations...")
        
        broad_search_results = {}
        
        for pattern in search_patterns:
            # Search across all analysis components
            count = cards_collection.count_documents({
                "$or": [
                    {f"analysis.components.{comp}": {"$regex": pattern, "$options": "i"}} 
                    for comp in [
                        "play_tips", "tactical_analysis", "synergy_analysis", 
                        "combo_suggestions", "power_level_assessment", "competitive_analysis",
                        "format_analysis", "mulligan_considerations", "sideboard_guide",
                        "budget_alternatives", "deck_archetypes", "meta_positioning",
                        "investment_outlook", "thematic_analysis", "historical_context",
                        "rules_clarifications", "art_flavor_analysis", "new_player_guide",
                        "advanced_interactions", "design_philosophy"
                    ]
                ]
            })
            
            if count > 0:
                broad_search_results[pattern] = count
        
        if broad_search_results:
            print(f"📊 Database-wide results:")
            for pattern, count in broad_search_results.items():
                print(f"   '{pattern}': {count} cards")
        else:
            print("ℹ️  No Swords variations found in entire database")
        
        # If we found typos, offer to fix them
        typo_patterns = ["Swords to Plowshops", "Swords to Plowshop", "[[Swords to Plowshops]]", "[[Swords to Plowshop]]"]
        typos_found = any(pattern in broad_search_results for pattern in typo_patterns)
        
        if typos_found:
            print(f"\n🔧 Would you like me to fix the typos? (This will replace incorrect variants with '[[Swords to Plowshares]]')")
        
    except Exception as e:
        print(f"❌ Error during check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_specific_card_swords()
