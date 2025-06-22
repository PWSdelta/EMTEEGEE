#!/usr/bin/env python3
"""
Reset Analysis for Testing
Reset some cards to create work for testing
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

def reset_analysis():
    """Reset analysis for some cards to create work"""
    print("🔄 Resetting analysis for testing...")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    db = client['emteegee_dev']
    cards = db.cards
      # Reset analysis for 100 cards to create work
    print("🎯 Resetting analysis for 100 cards...")
    
    # Get 100 cards that are fully analyzed
    cards_to_reset = list(cards.find(
        {'analysis.fully_analyzed': True}
    ).limit(100))
    
    if cards_to_reset:
        card_ids = [card['_id'] for card in cards_to_reset]
        
        result = cards.update_many(
            {'_id': {'$in': card_ids}},
            {
                '$set': {
                    'analysis.fully_analyzed': False,
                    'analysis.components': {}
                }
            }
        )
        
        print(f"✅ Reset {result.modified_count} cards")
    else:
        print("⚠️ No fully analyzed cards found to reset")
    
    # Verify work is now available
    available_for_work = cards.count_documents({
        'analysis.fully_analyzed': {'$ne': True}
    })
    
    print(f"🎯 Cards available for work: {available_for_work:,}")
    
    return available_for_work

if __name__ == "__main__":
    try:
        count = reset_analysis()
        print(f"\n✅ Analysis reset! {count:,} cards ready for processing")
        print("🚀 Workers should now detect available work")
    except Exception as e:
        print(f"❌ Error: {e}")
