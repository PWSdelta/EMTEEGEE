#!/usr/bin/env python
"""
Test statistics queries for the home page
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def test_statistics():
    cards_collection = get_cards_collection()
    
    print('=== STATISTICS DEBUG ===')
    total_cards = cards_collection.count_documents({})
    print(f'Total cards: {total_cards:,}')
    
    analyzed_count = cards_collection.count_documents({
        'analysis.components': {'$exists': True},
        '$expr': {
            '$eq': [
                {'$size': {'$objectToArray': '$analysis.components'}},
                20
            ]
        }
    })
    print(f'Fully analyzed (20 components): {analyzed_count:,}')
    
    synthesis_count = cards_collection.count_documents({
        'analysis.complete_analysis': {'$exists': True, '$ne': ''}
    })
    print(f'With synthesis: {synthesis_count:,}')
    
    partial_count = cards_collection.count_documents({
        'analysis.components': {'$exists': True},
        '$expr': {
            '$and': [
                {'$gt': [{'$size': {'$objectToArray': '$analysis.components'}}, 0]},
                {'$lt': [{'$size': {'$objectToArray': '$analysis.components'}}, 20]}
            ]
        }
    })
    print(f'Partial analysis (1-19 components): {partial_count:,}')
    
    # Test basic component count
    any_components = cards_collection.count_documents({
        'analysis.components': {'$exists': True}
    })
    print(f'Cards with any components: {any_components:,}')
    
    print('========================')

if __name__ == '__main__':
    test_statistics()
