#!/usr/bin/env python3
"""
Check deck size distribution and clean up small decks.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_decks_collection

def check_deck_sizes():
    """Check the current deck size distribution."""
    decks_collection = get_decks_collection()
    
    print(f"📊 Total decks in database: {decks_collection.count_documents({})}")
    
    # Get some sample decks to see what we have
    samples = list(decks_collection.find({}, {'name': 1, 'stats.total_count': 1}).limit(10))
    print("\n📋 Sample decks:")
    for deck in samples:
        total_count = deck.get('stats', {}).get('total_count', 0)
        name = deck.get('name', 'Unknown')
        print(f"  • {name}: {total_count} cards")
    
    # Count by size ranges
    under_20 = decks_collection.count_documents({'stats.total_count': {'$lt': 20}})
    twenty_to_59 = decks_collection.count_documents({'stats.total_count': {'$gte': 20, '$lt': 60}})
    sixty_plus = decks_collection.count_documents({'stats.total_count': {'$gte': 60}})
    
    print(f"\n📈 Deck size distribution:")
    print(f"   Under 20 cards: {under_20}")
    print(f"   20-59 cards: {twenty_to_59}")
    print(f"   60+ cards: {sixty_plus}")
    
    return under_20, twenty_to_59, sixty_plus

def cleanup_small_decks():
    """Remove decks with less than 60 cards."""
    decks_collection = get_decks_collection()
    
    # Find decks under 60 cards
    small_decks = list(decks_collection.find(
        {'stats.total_count': {'$lt': 60}}, 
        {'name': 1, 'stats.total_count': 1}
    ).limit(10))
    
    print("\n🗑️  Examples of decks to be removed:")
    for deck in small_decks:
        name = deck.get('name', 'Unknown')
        count = deck.get('stats', {}).get('total_count', 0)
        print(f"   • {name}: {count} cards")
    
    # Delete small decks
    result = decks_collection.delete_many({'stats.total_count': {'$lt': 60}})
    print(f"\n✅ Removed {result.deleted_count} decks with less than 60 cards")
    
    # Check final counts
    remaining = decks_collection.count_documents({})
    print(f"📊 Remaining decks: {remaining}")

if __name__ == "__main__":
    print("🔍 Checking deck sizes...")
    check_deck_sizes()
    
    print("\n" + "="*50)
    cleanup_small_decks()
