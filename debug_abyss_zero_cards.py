#!/usr/bin/env python3
"""
Debug why The Abyss might be showing 0 cards.
Test different scenarios and query combinations.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def debug_abyss_queries():
    """Test various query scenarios to understand the issue."""
    print("🔍 Debugging The Abyss - Zero Cards Issue")
    print("=" * 60)
    
    try:
        cards_collection = get_cards_collection()
        
        # Basic collection test
        total_cards = cards_collection.count_documents({})
        print(f"📊 Total cards in database: {total_cards:,}")
        
        if total_cards == 0:
            print("❌ No cards in database - need to import data first!")
            return
        
        # Test various collection queries
        print("\n🧪 Testing Collection Queries:")
        
        # 1. Test commanders query
        commanders_query = {
            '$and': [
                {'type': {'$regex': 'legendary', '$options': 'i'}},
                {'type': {'$regex': 'creature', '$options': 'i'}},
                {'edhrecRank': {'$exists': True, '$ne': None}}
            ]
        }
        commanders_count = cards_collection.count_documents(commanders_query)
        print(f"   🎭 Commanders: {commanders_count:,}")
        
        # 2. Test expensive cards query
        expensive_query = {
            '$or': [
                {'prices.usd': {'$gte': 20}},
                {'prices.eur': {'$gte': 18}}
            ]
        }
        expensive_count = cards_collection.count_documents(expensive_query)
        print(f"   💎 Expensive cards ($20+): {expensive_count:,}")
        
        # 3. Test budget cards query
        budget_query = {
            '$and': [
                {'$or': [
                    {'prices.usd': {'$lte': 1}},
                    {'prices.eur': {'$lte': 0.9}}
                ]},
                {'$or': [
                    {'prices.usd': {'$exists': True, '$ne': None}},
                    {'prices.eur': {'$exists': True, '$ne': None}}
                ]}
            ]
        }
        budget_count = cards_collection.count_documents(budget_query)
        print(f"   🏦 Budget cards (<$1): {budget_count:,}")
        
        # 4. Test EDHREC cards
        edhrec_query = {'edhrecRank': {'$exists': True, '$ne': None}}
        edhrec_count = cards_collection.count_documents(edhrec_query)
        print(f"   🏆 EDHREC ranked cards: {edhrec_count:,}")
        
        # 5. Test search queries
        print("\n🔍 Testing Search Queries:")
        
        search_tests = [
            "Lightning Bolt",
            "Bolt",
            "Blue",
            "Creature",
            "Land",
            "Artifact"
        ]
        
        for search_term in search_tests:
            search_query = {
                '$or': [
                    {'name': {'$regex': search_term, '$options': 'i'}},
                    {'text': {'$regex': search_term, '$options': 'i'}},
                    {'type': {'$regex': search_term, '$options': 'i'}},
                ]
            }
            search_count = cards_collection.count_documents(search_query)
            print(f"   🔎 '{search_term}': {search_count:,} matches")
        
        # 6. Test no-filter query (default abyss view)
        print("\n📋 Testing Default Queries:")
        
        # Empty query (should show all cards)
        all_cards_count = cards_collection.count_documents({})
        print(f"   📦 All cards (empty query): {all_cards_count:,}")
        
        # Sample a few cards to check data structure
        print("\n🧪 Sample Card Data:")
        sample_cards = list(cards_collection.find({}).limit(3))
        
        for i, card in enumerate(sample_cards, 1):
            print(f"\n   Card {i}: {card.get('name', 'Unknown')}")
            print(f"   - UUID: {card.get('uuid', 'N/A')}")
            print(f"   - Type: {card.get('type', 'N/A')}")
            print(f"   - Set: {card.get('setCode', 'N/A')}")
            print(f"   - Prices: USD ${card.get('prices', {}).get('usd', 'N/A')} | EUR €{card.get('prices', {}).get('eur', 'N/A')}")
            print(f"   - EDHREC Rank: {card.get('edhrecRank', 'N/A')}")
        
        # Check for problematic fields
        print("\n🔧 Field Analysis:")
        
        cards_with_prices = cards_collection.count_documents({
            '$or': [
                {'prices.usd': {'$exists': True, '$ne': None}},
                {'prices.eur': {'$exists': True, '$ne': None}}
            ]
        })
        print(f"   💰 Cards with pricing: {cards_with_prices:,}")
        
        cards_with_edhrec = cards_collection.count_documents({
            'edhrecRank': {'$exists': True, '$ne': None}
        })
        print(f"   📈 Cards with EDHREC rank: {cards_with_edhrec:,}")
        
        cards_with_images = cards_collection.count_documents({
            'imageUris': {'$exists': True, '$ne': None}
        })
        print(f"   🖼️  Cards with images: {cards_with_images:,}")
        
        print("\n✅ Debug complete! Check results above for any issues.")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_abyss_queries()
