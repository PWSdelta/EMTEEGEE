#!/usr/bin/env python
"""
Revert incorrect fully_analyzed flags - cards need 20 components, not 19.
"""

import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def revert_incorrect_flags():
    """Revert cards marked as fully_analyzed with only 19 components."""
    print("🔄 Reverting Incorrect Fully Analyzed Flags")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Find cards marked as fully_analyzed but have < 20 components
        pipeline = [
            {'$match': {
                'analysis.fully_analyzed': True,
                'analysis.components': {'$exists': True}
            }},
            {'$project': {
                'uuid': 1,
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
            {'$match': {'component_count': {'$lt': 20}}}
        ]
        
        incorrect_cards = list(cards_collection.aggregate(pipeline))
        
        print(f"🔍 Found {len(incorrect_cards)} incorrectly flagged cards:")
        
        for card in incorrect_cards:
            name = card['name']
            component_count = card['component_count']
            
            print(f"  - {name}: {component_count}/20 components (incorrectly marked as complete)")
            
            # Revert the fully_analyzed flag
            update_result = cards_collection.update_one(
                {'uuid': card['uuid']},
                {
                    '$set': {
                        'analysis.fully_analyzed': False,
                        'analysis.component_count': component_count,
                        'analysis.last_updated': datetime.now(timezone.utc).isoformat()
                    },
                    '$unset': {
                        'analysis.completed_at': ""
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print(f"    ✅ Reverted {name} to fully_analyzed=False")
            else:
                print(f"    ❌ Failed to revert {name}")
        
        # Verify the fix
        print("\n" + "=" * 50)
        print("📊 Final Status:")
        
        total_fully_analyzed = cards_collection.count_documents({'analysis.fully_analyzed': True})
        print(f"Cards marked as fully analyzed: {total_fully_analyzed}")
        
        if total_fully_analyzed > 0:
            examples = list(cards_collection.find(
                {'analysis.fully_analyzed': True},
                {'name': 1, 'analysis.component_count': 1}
            ).limit(3))
            
            print("Examples (should all have 20 components):")
            for card in examples:
                analysis = card.get('analysis', {})
                print(f"  - {card['name']}: {analysis.get('component_count', 0)} components")
        
        print(f"\n✅ Reverted {len(incorrect_cards)} incorrectly flagged cards")
        print("🎯 Analysis engine will now properly complete all 20 components!")
        
    except Exception as e:
        print(f"❌ Error during revert: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    revert_incorrect_flags()
