#!/usr/bin/env python
"""
Debug script to test the home view directly.
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def test_home_view_query():
    try:
        cards_collection = get_cards_collection()
        
        # Test the exact query from the home view
        fully_analyzed_cards = list(cards_collection.aggregate([
            {
                '$match': {
                    'analysis.components': {'$exists': True}
                }
            },
            {
                '$addFields': {
                    'component_count': {
                        '$cond': {
                            'if': {'$eq': [{'$type': '$analysis.components'}, 'object']},
                            'then': {'$size': {'$objectToArray': '$analysis.components'}},
                            'else': 0
                        }
                    }
                }
            },
            {
                '$match': {
                    'component_count': {'$eq': 20}  # Exactly 20 components = fully analyzed
                }
            },
            {
                '$sort': {
                    'edhrecRank': 1  # Sort by popularity
                }
            },
            {'$limit': 20}  # Show up to 20 cards
        ]))
        
        print(f"Found {len(fully_analyzed_cards)} fully analyzed cards")
        
        for i, card in enumerate(fully_analyzed_cards[:5], 1):
            name = card.get('name', 'Unknown')
            component_count = card.get('component_count', 0)
            print(f"{i}. {name} - Components: {component_count}")
        
        # Test statistics
        total_cards = cards_collection.count_documents({})
        analyzed_cards_count = len(fully_analyzed_cards)
        total_components = analyzed_cards_count * 20
        avg_components = 20 if analyzed_cards_count > 0 else 0
        
        print(f"\nStatistics:")
        print(f"Total cards: {total_cards:,}")
        print(f"Fully analyzed: {analyzed_cards_count}")
        print(f"Total components: {total_components:,}")
        print(f"Avg components: {avg_components}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_home_view_query()
