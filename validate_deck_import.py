#!/usr/bin/env python3
"""
Quick validation script for imported deck data.
Run this to verify the MongoDB deck import was successful.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_mongodb_collection

def validate_deck_import():
    """Validate the imported deck data."""
    try:
        # Get MongoDB collection
        decks = get_mongodb_collection('decks')
        
        # Count total decks
        total_decks = decks.count_documents({})
        print(f"✅ Total decks imported: {total_decks}")
        
        # Count decks by size
        valid_decks = decks.count_documents({"total_cards": {"$gte": 60}})
        invalid_decks = decks.count_documents({"total_cards": {"$lt": 60}})
        
        print(f"✅ Valid decks (60+ cards): {valid_decks}")
        print(f"⚠️  Invalid decks (<60 cards): {invalid_decks}")
        
        # Show format distribution
        print("\n📊 Format Distribution:")
        formats = decks.aggregate([
            {"$group": {"_id": "$format", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ])
        
        for format_data in formats:
            print(f"   {format_data['_id']}: {format_data['count']} decks")
        
        # Show sample deck
        print("\n🎯 Sample Deck:")
        sample_deck = decks.find_one({})
        if sample_deck:
            print(f"   Name: {sample_deck.get('name', 'Unknown')}")
            print(f"   Format: {sample_deck.get('format', 'Unknown')}")
            print(f"   Cards: {sample_deck.get('total_cards', 0)}")
            print(f"   Colors: {sample_deck.get('colors', [])}")
        
        # Check for decks with no cards
        empty_decks = decks.count_documents({"$or": [{"cards": {"$size": 0}}, {"cards": {"$exists": False}}]})
        print(f"\n🚨 Empty decks (no cards): {empty_decks}")
        
        print("\n🎉 Deck import validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating deck import: {e}")
        return False

if __name__ == "__main__":
    validate_deck_import()
