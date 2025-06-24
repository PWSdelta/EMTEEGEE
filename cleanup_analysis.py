#!/usr/bin/env python
"""
Clean up poor quality analysis components and reset analysis flags
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection
from datetime import datetime

def clean_analysis_data():
    """Remove all analysis components and reset analysis flags"""
    cards_collection = get_cards_collection()
    
    print("🧹 CLEANING UP ANALYSIS DATA...")
    print("=" * 50)
    
    # Get current stats before cleanup
    total_cards = cards_collection.count_documents({})
    cards_with_analysis = cards_collection.count_documents({'analysis': {'$exists': True}})
    
    print(f"📊 Before cleanup:")
    print(f"   Total cards: {total_cards:,}")
    print(f"   Cards with analysis: {cards_with_analysis:,}")
    
    # Option 1: Complete reset - remove all analysis data
    print(f"\n🗑️  Option 1: COMPLETE RESET (remove all analysis data)")
    print(f"   This will delete ALL analysis components and flags")
    
    # Option 2: Selective cleanup - keep some metadata but remove components
    print(f"\n🔧 Option 2: SELECTIVE CLEANUP (keep metadata, remove components)")
    print(f"   This will keep analysis timestamps but remove component content")
    
    choice = input("\nChoose option (1/2) or 'q' to quit: ").strip().lower()
    
    if choice == 'q':
        print("❌ Cleanup cancelled.")
        return
    
    elif choice == '1':
        # Complete reset
        print("\n⚠️  COMPLETE RESET - This will delete ALL analysis data!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == 'DELETE':
            result = cards_collection.update_many(
                {'analysis': {'$exists': True}},
                {'$unset': {'analysis': 1}}
            )
            print(f"✅ Complete reset done!")
            print(f"   Modified {result.modified_count} cards")
        else:
            print("❌ Reset cancelled.")
            return
    
    elif choice == '2':
        # Selective cleanup
        print("\n🔧 SELECTIVE CLEANUP - Removing components but keeping metadata...")
        confirm = input("Type 'CLEAN' to confirm: ").strip()
        
        if confirm == 'CLEAN':
            # Remove components but keep some metadata
            result = cards_collection.update_many(
                {'analysis.components': {'$exists': True}},
                {
                    '$unset': {
                        'analysis.components': 1,
                        'analysis.complete_analysis': 1,
                        'analysis.fully_analyzed': 1,
                        'analysis.component_count': 1
                    },
                    '$set': {
                        'analysis.last_cleanup': datetime.now(),
                        'analysis.cleanup_reason': 'Poor quality components - manual cleanup'
                    }
                }
            )
            print(f"✅ Selective cleanup done!")
            print(f"   Modified {result.modified_count} cards")
        else:
            print("❌ Cleanup cancelled.")
            return
    
    else:
        print("❌ Invalid choice. Cleanup cancelled.")
        return
    
    # Get stats after cleanup
    cards_with_analysis_after = cards_collection.count_documents({'analysis': {'$exists': True}})
    cards_with_components = cards_collection.count_documents({'analysis.components': {'$exists': True}})
    
    print(f"\n📊 After cleanup:")
    print(f"   Cards with analysis: {cards_with_analysis_after:,}")
    print(f"   Cards with components: {cards_with_components:,}")
    print(f"\n🎉 Cleanup completed successfully!")

def show_sample_components():
    """Show some sample components to assess quality"""
    cards_collection = get_cards_collection()
    
    print("\n🔍 SAMPLE ANALYSIS COMPONENTS:")
    print("=" * 50)
    
    # Get a few cards with components
    sample_cards = list(cards_collection.find(
        {'analysis.components': {'$exists': True}},
        {'name': 1, 'analysis.components': 1}
    ).limit(3))
    
    for card in sample_cards:
        print(f"\n📜 {card['name']}:")
        components = card.get('analysis', {}).get('components', {})
        
        for comp_type, comp_data in components.items():
            content = comp_data if isinstance(comp_data, str) else comp_data.get('content', str(comp_data))
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"  • {comp_type}: {preview}")
        
        print("-" * 40)

if __name__ == '__main__':
    print("🧹 EMTEEGEE ANALYSIS CLEANUP TOOL")
    print("=" * 50)
    
    # First show some samples
    show_sample_components()
    
    print(f"\n" + "=" * 50)
    clean_analysis_data()
