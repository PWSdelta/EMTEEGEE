#!/usr/bin/env python3
"""Test script to verify Scryfall enhancement worked properly."""

import os
import sys
from pymongo import MongoClient

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

# Import Django settings to get MongoDB config
from django.conf import settings

def test_card_enhancement(card_name="Sol Ring"):
    """Test that a card has been enhanced with Scryfall data."""
    print(f"Testing enhancement for: {card_name}")
    print("="*50)
      # Connect to MongoDB
    mongo_settings = settings.MONGODB_SETTINGS
    client = MongoClient(mongo_settings['host'])
    db = client[mongo_settings['db_name']]
    cards_collection = db.cards
    
    card = cards_collection.find_one({"name": card_name})
    if not card:
        print(f"❌ {card_name} not found in database")
        return
    
    print(f"✅ Found card: {card['name']}")
    print(f"📝 Mana Cost: {card.get('manaCost', 'N/A')}")
    print(f"🔗 Scryfall ID: {card.get('scryfallId', 'N/A')}")
    print(f"📊 EDHREC Rank: {card.get('edhrecRank', 'N/A')}")
    
    # Test pricing data
    if card.get('prices'):
        usd = card['prices'].get('usd')
        print(f"💰 USD Price: ${usd}" if usd else "💰 USD Price: N/A")
    else:
        print("💰 No pricing data")
    
    # Test images
    if card.get('images'):
        print(f"🖼️  Images: {len(card['images'])} available")
        for img_type, url in card['images'].items():
            print(f"   - {img_type}: {url[:50]}...")
    else:
        print("🖼️  No image data")
    
    # Test relationships
    if card.get('allParts'):
        print(f"🔗 Relationships: {len(card['allParts'])}")
        for part in card['allParts'][:3]:  # Show first 3
            print(f"   - {part.get('name', 'Unknown')}: {part.get('component', 'unknown')}")
    else:
        print("🔗 No relationship data")
    
    # Test legalities
    if card.get('legalities'):
        print(f"⚖️  Legalities: {len(card['legalities'])} formats")
        commander = card['legalities'].get('commander', 'unknown')
        print(f"   - Commander: {commander}")
    else:
        print("⚖️  No legality data")
    
    print(f"🕒 Enhanced At: {card.get('enhancedAt', 'Never')}")
    print("\n" + "="*50)

if __name__ == "__main__":
    # Test a few key cards
    test_card_enhancement("Sol Ring")
    test_card_enhancement("Lightning Bolt")
    test_card_enhancement("Black Lotus")
      # Show total stats
    mongo_settings = settings.MONGODB_SETTINGS
    client = MongoClient(mongo_settings['host'])
    db = client[mongo_settings['db_name']]
    cards_collection = db.cards
    
    total_cards = cards_collection.count_documents({})
    enhanced_cards = cards_collection.count_documents({"enhancedAt": {"$exists": True}})
    scryfall_cards = cards_collection.count_documents({"scryfallId": {"$exists": True}})
    
    print("\n📈 IMPORT STATISTICS:")
    print(f"Total cards: {total_cards}")
    print(f"Enhanced cards: {enhanced_cards}")
    print(f"With Scryfall ID: {scryfall_cards}")
    print(f"Enhancement rate: {(enhanced_cards/total_cards*100):.1f}%")
