#!/usr/bin/env python
"""
Fix cards with 20/20 components - mark them as fully analyzed.
"""

import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def fix_completed_cards():
    """Mark cards with 20/20 components as fully analyzed."""
    print("🔧 Fixing Completed Cards")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Find cards with 20/20 components but not marked as fully analyzed
        pipeline = [
            {'$match': {'analysis.components': {'$exists': True}}},
            {'$project': {
                'uuid': 1,
                'name': 1,
                'analysis.fully_analyzed': 1,
                'analysis.completed_at': 1,
                'component_count': {
                    '$size': {
                        '$filter': {
                            'input': {'$objectToArray': '$analysis.components'},
                            'cond': {'$ne': ['$$this.v', None]}
                        }
                    }
                }
            }},
            {'$match': {
                'component_count': 20,
                '$or': [
                    {'analysis.fully_analyzed': {'$ne': True}},
                    {'analysis.completed_at': {'$exists': False}}
                ]
            }}
        ]
        
        cards_to_fix = list(cards_collection.aggregate(pipeline))
        
        print(f"🔍 Found {len(cards_to_fix)} cards with 20/20 components that need fixing:")
        
        fixed_count = 0
        
        for card in cards_to_fix:
            name = card['name']
            component_count = card['component_count']
            uuid = card['uuid']
            
            print(f"  📋 {name} ({component_count}/20 components)")
            
            # Update the card to be properly marked as fully analyzed
            update_result = cards_collection.update_one(
                {'uuid': uuid},
                {
                    '$set': {
                        'analysis.fully_analyzed': True,
                        'analysis.completed_at': datetime.now(timezone.utc).isoformat(),
                        'analysis.component_count': 20,
                        'analysis.last_updated': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print(f"    ✅ Fixed {name}")
                fixed_count += 1
            else:
                print(f"    ❌ Failed to fix {name}")
        
        print(f"\n" + "=" * 50)
        print(f"📊 Results:")
        print(f"  Cards found: {len(cards_to_fix)}")
        print(f"  Cards fixed: {fixed_count}")
        
        # Check final status
        total_fully_analyzed = cards_collection.count_documents({'analysis.fully_analyzed': True})
        total_with_completed_at = cards_collection.count_documents({'analysis.completed_at': {'$exists': True}})
        
        print(f"  Total fully analyzed: {total_fully_analyzed}")
        print(f"  Total with completed_at: {total_with_completed_at}")
        
        print(f"\n✅ Fix complete! Cards with 20/20 components are now properly marked as fully analyzed.")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_completed_cards()
