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
    load_dotenv()
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    db = client['emteegee_dev']  # Always use this database name
    
    cards = db.cards
    
    # Get total card count
    total_cards = cards.count_documents({})
    print(f"📊 Total cards in database: {total_cards:,}")
    
    # Find cards that need analysis (using swarm manager's criteria)
    unanalyzed = cards.count_documents({
        '$or': [
            {'analysis.fully_analyzed': {'$ne': True}},
            {'analysis.components': {'$exists': False}}
        ]
    })
    print(f"🎯 Cards needing analysis: {unanalyzed:,}")
    
    if unanalyzed == 0:
        print("✅ All cards already have analysis! Resetting some for testing...")
        # Reset analysis structure for 50 cards to create work
        cards.update_many(
            {},
            {
                '$set': {
                    'analysis': {
                        'fully_analyzed': False,
                        'components': {}
                    }
                }
            }
        )
        print("🔄 Reset analysis structure for testing - work now available!")
        
        # Recount after reset
        unanalyzed = cards.count_documents({
            '$or': [
                {'analysis.fully_analyzed': {'$ne': True}},
                {'analysis.components': {'$exists': False}}
            ]
        })
    
    # Initialize analysis structure for cards that don't have it
    cards_without_analysis = cards.count_documents({
        'analysis': {'$exists': False}
    })
    
    if cards_without_analysis > 0:
        print(f"� Initializing analysis structure for {cards_without_analysis:,} cards...")
        cards.update_many(
            {'analysis': {'$exists': False}},
            {
                '$set': {
                    'analysis': {
                        'fully_analyzed': False,
                        'components': {}
                    }
                }
            }
        )
        print(f"✅ Initialized analysis structure")
    
    # Get sample of cards that now need work
    sample_cards = list(cards.find(
        {
            '$or': [
                {'analysis.fully_analyzed': {'$ne': True}},
                {'analysis.components': {'$exists': False}}
            ]
        },
        {'name': 1, 'mana_cost': 1, 'type_line': 1, 'oracle_text': 1, 'analysis': 1}
    ).limit(20))
    
    print(f"📝 Cards ready for analysis:")
    for i, card in enumerate(sample_cards[:5], 1):
        analysis_status = "No analysis" if 'analysis' not in card else f"{len(card['analysis'].get('components', {}))} components"
        print(f"   {i}. {card.get('name', 'Unknown')} - {analysis_status}")
    if len(sample_cards) > 5:
        print(f"   ... and {len(sample_cards) - 5} more")
    
    print(f"\n🎉 Work queue populated!")
    print(f"   {unanalyzed:,} cards ready for distributed analysis")
    print(f"   Desktop worker: GPU components (play_tips, combo_suggestions, etc.)")
    print(f"   Laptop worker: CPU components (thematic_analysis, historical_context, etc.)")
    
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
