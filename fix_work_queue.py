#!/usr/bin/env python3
"""
Fix Work Queue - Properly initialize analysis structure
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

def fix_work_queue():
    """Properly initialize analysis structure for SwarmManager"""
    print("🔧 Fixing work queue structure...")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    db = client['emteegee_dev']
    cards = db.cards
    
    # Check current state
    total_cards = cards.count_documents({})
    cards_with_analysis = cards.count_documents({'analysis': {'$exists': True}})
    
    print(f"📊 Total cards: {total_cards:,}")
    print(f"📊 Cards with analysis field: {cards_with_analysis:,}")
    
    # Initialize proper analysis structure
    print("🔄 Initializing analysis structure...")
    
    result = cards.update_many(
        {'analysis': {'$exists': False}},
        {
            '$set': {
                'analysis': {
                    'fully_analyzed': False,
                    'components': {},
                    'last_updated': None,
                    'worker_assignments': []
                }
            }
        }
    )
    
    print(f"✅ Updated {result.modified_count} cards with analysis structure")
    
    # Verify the structure
    sample_card = cards.find_one({'analysis': {'$exists': True}})
    if sample_card:
        print(f"📋 Sample analysis structure: {sample_card.get('analysis', {})}")
    
    # Count cards that should now be available for work
    available_for_work = cards.count_documents({
        'analysis.fully_analyzed': {'$ne': True}
    })
    
    print(f"🎯 Cards available for work: {available_for_work:,}")
    
    return available_for_work

if __name__ == "__main__":
    try:
        count = fix_work_queue()
        print(f"\n✅ Work queue fixed! {count:,} cards ready for processing")
        print("🚀 Workers should now detect available work")
    except Exception as e:
        print(f"❌ Error: {e}")
