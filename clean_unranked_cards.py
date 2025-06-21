#!/usr/bin/env python3
"""
Clean House: Delete Unranked Cards
Removes cards without EDHREC rankings to focus on playable cards only.
"""

import os
import sys

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

def clean_unranked_cards():
    """Remove cards that don't have EDHREC rankings."""
    
    cards_collection = get_cards_collection()
    
    print("🧹 CLEANING HOUSE: Removing unranked cards...")
    
    # Count what we're about to delete
    unranked_count = cards_collection.count_documents({
        'edhrecRank': {'$exists': False}
    })
    
    # Also check for null EDHREC ranks
    null_edhrec_count = cards_collection.count_documents({
        'edhrecRank': None
    })
    
    total_to_delete = unranked_count + null_edhrec_count
    
    # Count what we're keeping  
    ranked_count = cards_collection.count_documents({
        'edhrecRank': {'$exists': True, '$ne': None, '$type': 'number'}
    })
    
    print(f"📊 CLEANUP ANALYSIS:")
    print(f"   📈 Keeping: {ranked_count:,} ranked cards (the good stuff)")
    print(f"   🗑️  Deleting: {total_to_delete:,} unranked cards (the junk)")
    print(f"   📈 Efficiency: {(ranked_count/(ranked_count+total_to_delete)*100):.1f}% cards retained")
    
    # Confirm deletion
    print(f"\n⚠️  This will PERMANENTLY DELETE {total_to_delete:,} cards!")
    response = input("Type 'DELETE' to confirm: ")
    
    if response != 'DELETE':
        print("❌ Cancelled. No cards deleted.")
        return
    
    print(f"\n🔥 DELETING {total_to_delete:,} unranked cards...")
    
    # Delete unranked cards
    result1 = cards_collection.delete_many({
        'edhrecRank': {'$exists': False}
    })
    
    # Delete null EDHREC ranks
    result2 = cards_collection.delete_many({
        'edhrecRank': None
    })
    
    total_deleted = result1.deleted_count + result2.deleted_count
    
    # Final count
    final_count = cards_collection.count_documents({})
    
    print(f"\n✅ CLEANUP COMPLETE!")
    print(f"   🗑️  Deleted: {total_deleted:,} unranked cards")
    print(f"   📈 Remaining: {final_count:,} ranked cards")
    print(f"   🎯 Database now {(total_deleted/(total_deleted+final_count)*100):.1f}% smaller!")
    
    print(f"\n🚀 BENEFITS:")
    print(f"   ⚡ Faster queries and analysis")
    print(f"   🎯 100% focus on playable cards") 
    print(f"   💾 Reduced storage and memory usage")
    print(f"   🧹 Cleaner, more manageable dataset")
    
    return {
        'deleted': total_deleted,
        'remaining': final_count,
        'efficiency_gain': total_deleted/(total_deleted+final_count)*100
    }

if __name__ == "__main__":
    stats = clean_unranked_cards()
    if stats:
        print(f"\nStats: {stats}")
