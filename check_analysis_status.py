#!/usr/bin/env python
"""
Diagnostic script to check the analysis status of cards in the database.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def check_analysis_status():
    """Check the current analysis status of cards."""
    print("🔍 EMTEEGEE Analysis Status Check")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Get total card count
        total_cards = cards_collection.count_documents({})
        print(f"📊 Total cards in database: {total_cards:,}")
        
        # Check for analysis field structure
        print("\n🔬 Analysis Field Structure:")
        sample_card = cards_collection.find_one({}, {'analysis': 1, 'name': 1})
        if sample_card:
            print(f"Sample card: {sample_card.get('name', 'Unknown')}")
            analysis = sample_card.get('analysis', {})
            if analysis:
                print(f"Analysis keys: {list(analysis.keys())}")
                if 'fully_analyzed' in analysis:
                    print(f"  - fully_analyzed: {analysis['fully_analyzed']}")
                if 'components' in analysis:
                    components = analysis['components']
                    print(f"  - components: {len(components)} items")
                    print(f"  - component keys: {list(components.keys())}")
            else:
                print("  - No analysis data found")
        else:
            print("  - No cards found in database")
        
        # Check various analysis states
        print("\n📈 Analysis States:")
        
        # Cards with any analysis data
        cards_with_analysis = cards_collection.count_documents({'analysis': {'$exists': True}})
        print(f"Cards with analysis field: {cards_with_analysis:,}")
        
        # Cards with analysis.fully_analyzed = true
        fully_analyzed_count = cards_collection.count_documents({'analysis.fully_analyzed': True})
        print(f"Cards with fully_analyzed=True: {fully_analyzed_count:,}")
        
        # Cards with analysis.fully_analyzed = false
        partially_analyzed_count = cards_collection.count_documents({'analysis.fully_analyzed': False})
        print(f"Cards with fully_analyzed=False: {partially_analyzed_count:,}")
        
        # Cards with components
        cards_with_components = cards_collection.count_documents({'analysis.components': {'$exists': True}})
        print(f"Cards with components: {cards_with_components:,}")
        
        # Cards with completed_at
        cards_with_completion = cards_collection.count_documents({'analysis.completed_at': {'$exists': True}})
        print(f"Cards with completed_at: {cards_with_completion:,}")
        
        # Get some examples of cards with analysis
        print("\n📋 Sample Cards with Analysis:")
        sample_analyzed = list(cards_collection.find(
            {'analysis': {'$exists': True}},
            {'name': 1, 'analysis.fully_analyzed': 1, 'analysis.components': 1, 'analysis.completed_at': 1}
        ).limit(5))
        
        for i, card in enumerate(sample_analyzed, 1):
            analysis = card.get('analysis', {})
            print(f"{i}. {card.get('name', 'Unknown')}")
            print(f"   - fully_analyzed: {analysis.get('fully_analyzed', 'Not set')}")
            print(f"   - completed_at: {analysis.get('completed_at', 'Not set')}")
            components = analysis.get('components', {})
            if components:
                completed_components = [k for k, v in components.items() if v]
                print(f"   - components: {len(completed_components)}/{len(components)} completed")
                print(f"   - completed: {completed_components[:3]}{'...' if len(completed_components) > 3 else ''}")
            else:
                print(f"   - components: None")
            print()
        
        # Check for any cards that might be "fully analyzed" but not marked as such
        print("🔍 Checking for unmarked fully analyzed cards:")
        
        # Look for cards with many completed components but not marked as fully_analyzed
        pipeline = [
            {'$match': {'analysis.components': {'$exists': True}}},
            {'$project': {
                'name': 1,
                'analysis.fully_analyzed': 1,
                'component_count': {
                    '$size': {
                        '$filter': {
                            'input': {'$objectToArray': '$analysis.components'},
                            'cond': {'$ne': ['$$this.v', None]}
                        }
                    }
                }
            }},
            {'$match': {'component_count': {'$gte': 5}}},  # Cards with 5+ components
            {'$sort': {'component_count': -1}},
            {'$limit': 10}
        ]
        
        potentially_complete = list(cards_collection.aggregate(pipeline))
        
        if potentially_complete:
            print(f"Cards with 5+ completed components:")
            for card in potentially_complete:
                fully_analyzed = card.get('analysis', {}).get('fully_analyzed', False)
                print(f"  - {card['name']}: {card['component_count']} components, fully_analyzed={fully_analyzed}")
        else:
            print("  - No cards found with 5+ completed components")
        
        print("\n✅ Analysis check complete!")
        
    except Exception as e:
        print(f"❌ Error during analysis check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_analysis_status()
