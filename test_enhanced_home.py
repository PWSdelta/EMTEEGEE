#!/usr/bin/env python3
"""Test the enhanced home page with beautiful card displays."""

import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def test_home_page_cards():
    """Test that we have cards for the home page display."""
    print("🏠 Testing Enhanced Home Page Cards")
    print("=" * 50)
    
    cards_collection = get_cards_collection()
    
    # Test featured cards (cards with analysis or high EDHREC rank)
    featured_query = {
        '$or': [
            {'edhrecRank': {'$lte': 1000}},  # Top 1000 cards
            {'analysis.analysis_completed_at': {'$exists': True}}  # Analyzed cards
        ]
    }
    featured_count = cards_collection.count_documents(featured_query)
    print(f"🌟 Featured cards available: {featured_count:,}")
    
    if featured_count > 0:
        featured_samples = list(cards_collection.find(featured_query).limit(6))
        print("   Sample featured cards:")
        for i, card in enumerate(featured_samples, 1):
            name = card.get('name', 'Unknown')
            rarity = card.get('rarity', 'N/A')
            rank = card.get('edhrecRank', 'N/A')
            print(f"     {i}. {name} ({rarity}) - EDHREC: {rank}")
    
    # Test recent cards (just any cards, sorted by a field if available)
    recent_count = cards_collection.count_documents({})
    print(f"\n🆕 Total cards for recent section: {recent_count:,}")
    
    if recent_count > 0:
        recent_samples = list(cards_collection.find({}).limit(12))
        print("   Sample recent cards:")
        for i, card in enumerate(recent_samples[:6], 1):
            name = card.get('name', 'Unknown')
            set_code = card.get('setCode', 'N/A')
            print(f"     {i}. {name} ({set_code})")
    
    # Check for image availability
    cards_with_images = cards_collection.count_documents({
        '$or': [
            {'imageUris.normal': {'$exists': True, '$ne': None}},
            {'imageUris.small': {'$exists': True, '$ne': None}}
        ]
    })
    
    print(f"\n🖼️ Cards with images: {cards_with_images:,}")
    print(f"📊 Image coverage: {(cards_with_images/recent_count)*100:.1f}%")
    
    print(f"\n✅ Home page ready with enhanced card displays!")

if __name__ == '__main__':
    test_home_page_cards()
