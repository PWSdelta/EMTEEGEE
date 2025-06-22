#!/usr/bin/env python3
"""
Import deck data from JSON files into MongoDB.
"""

import os
import json
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_decks_collection

def import_deck_files():
    """Import all deck JSON files into MongoDB."""
    
    deck_files_dir = Path("downloads/deck_files")
    decks_collection = get_decks_collection()
    
    print(f"🔍 Looking for deck files in {deck_files_dir}")
    
    if not deck_files_dir.exists():
        print(f"❌ Directory {deck_files_dir} not found!")
        return
    
    json_files = list(deck_files_dir.glob("*.json"))
    print(f"📋 Found {len(json_files)} JSON files")
    
    imported_count = 0
    error_count = 0
    
    for json_file in json_files:
        try:
            # Skip the HTML file and sample deck
            if json_file.name in ['decks_list.html', 'sample_deck.json']:
                continue
                
            print(f"📖 Processing {json_file.name}...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)
            
            # Extract the actual deck data
            if 'data' in deck_data:
                deck = deck_data['data']
            else:
                deck = deck_data
              # Add some metadata
            deck['_id'] = deck.get('code', json_file.stem)
            deck['file_name'] = json_file.name
            deck['imported_at'] = datetime.now()
            
            # Calculate some useful stats
            main_board_count = sum(card.get('count', 0) for card in deck.get('mainBoard', []))
            side_board_count = sum(card.get('count', 0) for card in deck.get('sideBoard', []))
            commander_count = sum(card.get('count', 0) for card in deck.get('commander', []))
            
            deck['stats'] = {
                'main_board_count': main_board_count,
                'side_board_count': side_board_count,
                'commander_count': commander_count,
                'total_count': main_board_count + side_board_count + commander_count
            }
            
            # Try to insert/update the deck
            result = decks_collection.replace_one(
                {'_id': deck['_id']}, 
                deck, 
                upsert=True
            )
            
            if result.upserted_id:
                print(f"✅ Imported: {deck.get('name', 'Unknown')} ({main_board_count} cards)")
            else:
                print(f"🔄 Updated: {deck.get('name', 'Unknown')} ({main_board_count} cards)")
            
            imported_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            error_count += 1
            continue
    
    print(f"\n🎯 Import Summary:")
    print(f"   ✅ Successfully imported: {imported_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📊 Total processed: {len(json_files)}")
    
    # Show some sample data
    sample_decks = list(decks_collection.find({}, {'name': 1, 'type': 1, 'stats': 1}).limit(5))
    print(f"\n📋 Sample decks:")
    for deck in sample_decks:
        print(f"   • {deck.get('name', 'Unknown')} ({deck.get('type', 'Unknown')} - {deck.get('stats', {}).get('total_count', 0)} cards)")

if __name__ == "__main__":
    from datetime import datetime
    import_deck_files()
