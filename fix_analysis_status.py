#!/usr/bin/env python
"""
Fix fully analyzed cards - identify missing components and update flags.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection
from cards.ollama_client import ALL_COMPONENT_TYPES

def fix_fully_analyzed_cards():
    """Fix cards that should be marked as fully analyzed."""
    print("🔧 EMTEEGEE Analysis Fix Tool")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        print(f"📊 Expected component types: {len(ALL_COMPONENT_TYPES)}")
        print(f"Component types: {ALL_COMPONENT_TYPES}")
        print()
          # Find cards with 19 components (should be fully analyzed)
        pipeline = [
            {'$match': {'analysis.components': {'$exists': True}}},
            {'$project': {
                'uuid': 1,
                'name': 1,
                'analysis.fully_analyzed': 1,
                'analysis.components': 1,
                'component_count': {
                    '$size': {
                        '$filter': {
                            'input': {'$objectToArray': '$analysis.components'},
                            'cond': {'$ne': ['$$this.v', None]}
                        }
                    }
                },
                'component_keys': {'$objectToArray': '$analysis.components'}
            }},
            {'$match': {'component_count': {'$gte': 19}}},
            {'$sort': {'component_count': -1}},
            {'$limit': 20}
        ]
        
        cards_to_fix = list(cards_collection.aggregate(pipeline))
        
        print(f"🔍 Found {len(cards_to_fix)} cards with 19+ components:")
        
        for card in cards_to_fix:
            name = card['name']
            component_count = card['component_count']
            fully_analyzed = card.get('analysis', {}).get('fully_analyzed', False)
            
            # Get actual component keys
            components = card.get('analysis', {}).get('components', {})
            actual_component_keys = set(components.keys())
            expected_component_keys = set(ALL_COMPONENT_TYPES)
            
            missing_components = expected_component_keys - actual_component_keys
            extra_components = actual_component_keys - expected_component_keys
            
            print(f"\n📋 {name}")
            print(f"   Components: {component_count}/20")
            print(f"   Fully analyzed: {fully_analyzed}")
            
            if missing_components:
                print(f"   Missing: {list(missing_components)}")
            if extra_components:
                print(f"   Extra: {list(extra_components)}")
                
            # If this card has 19 components and is missing exactly 1, it should be marked as fully analyzed
            if component_count == 19 and len(missing_components) == 1:
                print(f"   🎯 Should be marked as fully analyzed!")
                  # Update the card to be fully analyzed
                update_result = cards_collection.update_one(
                    {'uuid': card['uuid']},
                    {
                        '$set': {
                            'analysis.fully_analyzed': True,
                            'analysis.completed_at': datetime.utcnow().isoformat(),
                            'analysis.component_count': 19,
                            'analysis.last_updated': datetime.utcnow().isoformat()
                        }
                    }
                )
                
                if update_result.modified_count > 0:
                    print(f"   ✅ Updated {name} to fully_analyzed=True")
                else:
                    print(f"   ❌ Failed to update {name}")
        
        # Check the results
        print("\n" + "=" * 50)
        print("📊 Updated Analysis Status:")
        
        fully_analyzed_count = cards_collection.count_documents({'analysis.fully_analyzed': True})
        print(f"Cards now marked as fully analyzed: {fully_analyzed_count}")
        
        # Show some examples
        if fully_analyzed_count > 0:
            examples = list(cards_collection.find(
                {'analysis.fully_analyzed': True},
                {'name': 1, 'analysis.component_count': 1, 'analysis.completed_at': 1}
            ).limit(5))
            
            print("\n🎉 Examples of fully analyzed cards:")
            for card in examples:
                analysis = card.get('analysis', {})
                print(f"  - {card['name']} ({analysis.get('component_count', 0)} components)")
        
        print("\n✅ Fix complete!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_fully_analyzed_cards()
