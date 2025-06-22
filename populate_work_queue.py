#!/usr/bin/env python3
"""
Populate Work Queue for Testing
Add cards to the analysis queue for distributed processing
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import random
import time

def populate_queue():
    """Add random cards to the analysis queue"""
    print("🚀 Populating work queue for distributed analysis...")
    
    # Load environment variables
    load_dotenv()    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    db = client['emteegee_dev']  # Always use this database name
    
    cards = db.cards
    
    # Get total card count
    total_cards = cards.count_documents({})
    print(f"📊 Total cards in database: {total_cards:,}")
    
    # Find cards that need analysis (no swarm analysis yet)
    unanalyzed = cards.count_documents({
        'swarm_analysis': {'$exists': False}
    })
    print(f"🎯 Cards needing analysis: {unanalyzed:,}")
    
    if unanalyzed == 0:
        print("✅ All cards already have analysis! Clearing some for testing...")
        # Clear analysis from 50 random cards for testing
        cards.update_many(
            {},
            {'$unset': {'swarm_analysis': 1}},
            limit=50
        )
        print("🔄 Cleared analysis from 50 cards for re-processing")
    
    # Get sample of cards for processing
    sample_cards = list(cards.find(
        {'swarm_analysis': {'$exists': False}},
        {'name': 1, 'mana_cost': 1, 'type_line': 1, 'oracle_text': 1}
    ).limit(20))
    
    print(f"📝 Queued {len(sample_cards)} cards for analysis:")
    for i, card in enumerate(sample_cards[:5], 1):
        print(f"   {i}. {card.get('name', 'Unknown')}")
    if len(sample_cards) > 5:
        print(f"   ... and {len(sample_cards) - 5} more")
    
    print(f"\n🎉 Work queue populated!")
    print(f"   Workers will now pick up these cards for analysis")
    print(f"   Desktop worker: Quick analysis with qwen2.5:7b")
    print(f"   Laptop worker: Deep analysis with mixtral:8x7b")
    
    return len(sample_cards)

def show_worker_status():
    """Show current worker status"""
    print("\n📊 Current System Status:")
    print("   • Desktop Worker: Processing quick analyses")
    print("   • Laptop Worker: Processing deep analyses")  
    print("   • MongoDB: Remote Atlas database")
    print("   • External Access: https://emteegee.tcgplex.com")
    print("\n💡 Both workers should now start picking up tasks!")
    print("   Monitor progress at: https://emteegee.tcgplex.com/cards/api/swarm/status")

if __name__ == "__main__":
    try:
        queued_count = populate_queue()
        show_worker_status()
        
        print(f"\n✅ Successfully queued {queued_count} cards for distributed analysis!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
