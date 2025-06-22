#!/usr/bin/env python3
"""Clean problematic analysis components and let the system re-analyze."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def clean_problematic_components():
    """Delete problematic components and mark for re-analysis."""
    print("🧹 Cleaning Problematic Analysis Components")
    print("=" * 60)
    
    try:
        from cards.models import get_cards_collection
        cards_collection = get_cards_collection()
        
        # Define problematic patterns to look for
        problematic_patterns = [
            "Plowshops",  # Should be "Plowshares"
            "[[[]",       # Malformed card links
            "]]]",        # Malformed card links
            "[[]]",       # Empty card links
            "{{",         # Wrong bracket type
            "}}",         # Wrong bracket type
        ]
        
        total_cleaned = 0
        cards_affected = 0
        
        print("🔍 Searching for cards with problematic components...")
        
        # Search through all cards with analysis data
        for card in cards_collection.find({"analysis.components": {"$exists": True}}):
            card_name = card.get('name', 'Unknown')
            components = card.get('analysis', {}).get('components', {})
            
            components_to_delete = []
            
            # Check each component for problematic patterns
            for component_name, component_text in components.items():
                if component_text and isinstance(component_text, str):
                    for pattern in problematic_patterns:
                        if pattern in component_text:
                            components_to_delete.append(component_name)
                            print(f"   🚨 Found '{pattern}' in {card_name} - {component_name}")
                            break
            
            # Delete problematic components
            if components_to_delete:
                cards_affected += 1
                total_cleaned += len(components_to_delete)
                
                # Remove the problematic components
                update_operations = {}
                for comp in components_to_delete:
                    update_operations[f"analysis.components.{comp}"] = None
                
                # Also mark as not fully analyzed so it gets re-queued
                update_operations["analysis.fully_analyzed"] = False
                
                # Update the card
                result = cards_collection.update_one(
                    {"_id": card["_id"]},
                    {"$unset": {f"analysis.components.{comp}": "" for comp in components_to_delete},
                     "$set": {"analysis.fully_analyzed": False}}
                )
                
                if result.modified_count > 0:
                    print(f"   ✅ Cleaned {len(components_to_delete)} components from {card_name}")
                    for comp in components_to_delete:
                        print(f"      - Deleted: {comp}")
                else:
                    print(f"   ❌ Failed to clean {card_name}")
        
        print(f"\n🎉 Cleaning Complete!")
        print(f"   📊 Cards affected: {cards_affected}")
        print(f"   🧹 Components cleaned: {total_cleaned}")
        print(f"   🔄 Cards marked for re-analysis: {cards_affected}")
        
        if cards_affected > 0:
            print(f"\n💡 Next steps:")
            print(f"   1. Run: python manage.py whole_shebang --max-cards {cards_affected}")
            print(f"   2. The enhanced system will re-analyze with better quality")
            print(f"   3. Fresh components will replace the problematic ones")
        else:
            print(f"\n✅ No problematic components found - system is clean!")
            
    except Exception as e:
        print(f"❌ Error during cleaning: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_problematic_components()
