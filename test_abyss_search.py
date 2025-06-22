#!/usr/bin/env python3
"""Test the simplified Abyss search functionality."""

import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def test_search_terms():
    """Test various search terms to ensure comprehensive coverage."""
    print("🔍 Testing Abyss Search Functionality")
    print("=" * 50)
    
    cards_collection = get_cards_collection()
    
    test_searches = [
        "Lightning Bolt",           # Exact card name
        "lightning",               # Partial name
        "instant",                 # Card type
        "red",                     # Color in text
        "Rebecca Guay",            # Artist
        "Zendikar",               # Set name
        "ZEN",                    # Set code
        "flying",                 # Keyword
        "draw a card",            # Text search
        "legendary creature",     # Type combination
        "planeswalker",          # Type
        "mana",                  # Common text
        "sacrifice",             # Ability word
        "enters the battlefield"  # Rules text
    ]
    
    for search_term in test_searches:
        # Simulate the search logic from the view
        search_terms = search_term.split()
        search_conditions = []
        
        for term in search_terms:
            search_conditions.append({
                '$or': [
                    {'name': {'$regex': term, '$options': 'i'}},
                    {'text': {'$regex': term, '$options': 'i'}},
                    {'type': {'$regex': term, '$options': 'i'}},
                    {'artist': {'$regex': term, '$options': 'i'}},
                    {'setName': {'$regex': term, '$options': 'i'}},
                    {'setCode': {'$regex': term, '$options': 'i'}},
                    {'keywords': {'$in': [term]}},
                    {'flavorText': {'$regex': term, '$options': 'i'}},
                    {'manaCost': {'$regex': term, '$options': 'i'}},
                    {'subtypes': {'$in': [term]}},
                    {'supertypes': {'$in': [term]}}
                ]
            })
        
        query = {'$and': search_conditions} if search_conditions else {}
        count = cards_collection.count_documents(query)
        
        print(f"🎯 '{search_term}': {count:,} results")
        
        if count > 0 and count < 10:
            # Show some sample results for smaller result sets
            samples = list(cards_collection.find(query).limit(3))
            for sample in samples:
                print(f"   - {sample.get('name', 'Unknown')}")
    
    print(f"\n✅ Search testing complete!")

if __name__ == '__main__':
    test_search_terms()
