#!/usr/bin/env python3
"""
Simple EDHREC Priority Setter
Just gets EDHREC ranks and sets analysis priorities based on popularity.
Fast and simple - no over-engineering.
"""

import os
import sys
import requests
from datetime import datetime, timezone
from pymongo import UpdateOne

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

def get_edhrec_ranks_from_scryfall():
    """Get just the EDHREC ranks from Scryfall bulk data."""
    print("🎯 Fetching EDHREC ranks from Scryfall...")
    
    # Get bulk data info
    response = requests.get("https://api.scryfall.com/bulk-data", timeout=30)
    response.raise_for_status()
    bulk_data = response.json()['data']
    
    # Find oracle cards dataset
    oracle_dataset = None
    for item in bulk_data:
        if item.get('type') == 'oracle_cards':
            oracle_dataset = item
            break
    
    if not oracle_dataset:
        raise ValueError("Oracle cards dataset not found")
    
    print(f"📥 Downloading EDHREC data from Scryfall...")
    
    # Download and extract just what we need
    response = requests.get(oracle_dataset['download_uri'], stream=True, timeout=60)
    response.raise_for_status()
    
    import json
    cards_data = json.loads(response.content)
    
    # Extract only name and EDHREC rank
    edhrec_data = {}
    for card in cards_data:
        name = card.get('name')
        edhrec_rank = card.get('edhrec_rank')
        if name:
            edhrec_data[name] = edhrec_rank
    
    print(f"✅ Extracted EDHREC data for {len(edhrec_data)} cards")
    return edhrec_data

def set_simple_priorities():
    """Set simple analysis priorities based on EDHREC popularity."""
    
    # Get EDHREC ranks
    edhrec_data = get_edhrec_ranks_from_scryfall()
    
    # Get our cards collection
    cards_collection = get_cards_collection()
    
    print("🔍 Finding cards that need analysis priorities...")
    
    # Get all unanalyzed cards
    unanalyzed_cards = list(cards_collection.find({
        'analysis': {'$exists': False},
        'analysisRequested': {'$ne': True}
    }, {'name': 1}))
    
    print(f"📋 Found {len(unanalyzed_cards)} cards needing analysis")
    
    # Sort cards by EDHREC popularity
    ranked_cards = []
    unranked_cards = []
    
    for card in unanalyzed_cards:
        card_name = card['name']
        edhrec_rank = edhrec_data.get(card_name)
        
        if edhrec_rank is not None:
            ranked_cards.append((card, edhrec_rank))
        else:
            unranked_cards.append(card)
    
    # Sort ranked cards by popularity (lower rank = more popular)
    ranked_cards.sort(key=lambda x: x[1])
    
    print(f"🏆 {len(ranked_cards)} cards have EDHREC rankings")
    print(f"❓ {len(unranked_cards)} cards are unranked")
    
    # Set priorities in batches
    batch_size = 2357
    all_updates = []
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Priority 1: Top EDHREC cards (ranks 1-1000)
    priority_1_cards = [card for card, rank in ranked_cards if rank <= 1000]
    for card in priority_1_cards:
        all_updates.append(UpdateOne(
            {'_id': card['_id']},
            {'$set': {'priority': 1, 'priorityReason': 'Top 1000 EDHREC', 'priorityUpdatedAt': timestamp}}
        ))
    
    # Priority 2: Popular EDHREC cards (ranks 1001-5000)
    priority_2_cards = [card for card, rank in ranked_cards if 1001 <= rank <= 5000]
    for card in priority_2_cards:
        all_updates.append(UpdateOne(
            {'_id': card['_id']},
            {'$set': {'priority': 2, 'priorityReason': 'Popular EDHREC', 'priorityUpdatedAt': timestamp}}
        ))
    
    # Priority 3: Ranked EDHREC cards (ranks 5001+)
    priority_3_cards = [card for card, rank in ranked_cards if rank > 5000]
    for card in priority_3_cards:
        all_updates.append(UpdateOne(
            {'_id': card['_id']},
            {'$set': {'priority': 3, 'priorityReason': 'Ranked EDHREC', 'priorityUpdatedAt': timestamp}}
        ))
    
    # Priority 4: Unranked cards
    for card in unranked_cards:
        all_updates.append(UpdateOne(
            {'_id': card['_id']},
            {'$set': {'priority': 4, 'priorityReason': 'Unranked', 'priorityUpdatedAt': timestamp}}
        ))
    
    print(f"\n📊 PRIORITY DISTRIBUTION:")
    print(f"   Priority 1 (Top 1000): {len(priority_1_cards)} cards")
    print(f"   Priority 2 (Popular): {len(priority_2_cards)} cards") 
    print(f"   Priority 3 (Ranked): {len(priority_3_cards)} cards")
    print(f"   Priority 4 (Unranked): {len(unranked_cards)} cards")
    
    # Execute updates in batches
    print(f"\n🚀 Updating {len(all_updates)} cards with priorities...")
    
    for i in range(0, len(all_updates), batch_size):
        batch = all_updates[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(all_updates) + batch_size - 1) // batch_size
        
        print(f"   Batch {batch_num}/{total_batches}: {len(batch)} updates")
        
        try:
            result = cards_collection.bulk_write(batch, ordered=False)
            print(f"   ✅ Updated {result.modified_count} cards")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 PRIORITY SETUP COMPLETE!")
    print(f"Analysis queue now prioritized by EDHREC popularity!")
    
    return {
        'priority_1': len(priority_1_cards),
        'priority_2': len(priority_2_cards), 
        'priority_3': len(priority_3_cards),
        'priority_4': len(unranked_cards),
        'total_updated': len(all_updates)
    }

if __name__ == "__main__":
    stats = set_simple_priorities()
    print(f"\nStats: {stats}")
