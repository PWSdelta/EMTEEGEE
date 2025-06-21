#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced Scryfall import with intelligent merging.
Shows how existing card data is preserved while being enhanced with Scryfall data.
"""

import json
from datetime import datetime, timezone
from import_scryfall_data import ScryfallBulkImporter

def create_test_data():
    """Create sample test data to demonstrate merging."""
    
    # Sample existing card in our database (with analysis data)
    existing_card = {
        '_id': 'test_id_123',
        'uuid': 'existing-uuid-123',
        'name': 'Lightning Bolt',
        'manaCost': '{R}',
        'manaValue': 1,
        'type': 'Instant',
        'text': 'Lightning Bolt deals 3 damage to any target.',
        'colors': ['R'],
        'rarity': 'common',
        'setCode': 'LEA',
        
        # Our app-specific data that should be preserved
        'analysis': 'This is a classic burn spell with great efficiency...',
        'analysisRequested': True,
        'analysisRequestedAt': '2024-01-15T10:30:00Z',
        'priority': 'high',
        'requestCount': 3,
        'importedAt': '2024-01-01T00:00:00Z'
    }
    
    # Sample Scryfall data for the same card (with enhanced info)
    scryfall_data = {
        'id': '60a9d2d3-c0b8-4f1e-9f0b-2c3d4e5f6789',
        'oracle_id': 'oracle-12345',
        'name': 'Lightning Bolt',
        'mana_cost': '{R}',
        'cmc': 1,
        'type_line': 'Instant',
        'oracle_text': 'Lightning Bolt deals 3 damage to any target.',
        'colors': ['R'],
        'color_identity': ['R'],
        'keywords': [],
        'legalities': {
            'standard': 'not_legal',
            'pioneer': 'legal',
            'modern': 'legal',
            'legacy': 'legal',
            'vintage': 'legal',
            'commander': 'legal'
        },
        'rarity': 'common',
        'set': 'LEA',
        'set_name': 'Limited Edition Alpha',
        'collector_number': '161',
        'artist': 'Christopher Rush',
        'released_at': '1993-08-05',
        'scryfall_uri': 'https://scryfall.com/card/lea/161/lightning-bolt',
        'image_uris': {
            'small': 'https://cards.scryfall.io/small/front/6/0/60a9d2d3.jpg',
            'normal': 'https://cards.scryfall.io/normal/front/6/0/60a9d2d3.jpg',
            'large': 'https://cards.scryfall.io/large/front/6/0/60a9d2d3.jpg'
        },
        'prices': {
            'usd': '0.25',
            'usd_foil': '2.50',
            'eur': '0.20',
            'tix': '0.03'
        },
        'purchase_uris': {
            'tcgplayer': 'https://www.tcgplayer.com/...',
            'cardmarket': 'https://www.cardmarket.com/...'
        }
    }
    
    return existing_card, scryfall_data

def test_intelligent_merge():
    """Test the intelligent merge functionality."""
    print("🧪 Testing Scryfall Intelligent Merge")
    print("=" * 50)
    
    # Get test data
    existing_card, scryfall_data = create_test_data()
    
    # Create importer instance
    importer = ScryfallBulkImporter()
    
    # Perform the merge
    merged_card = importer.merge_card_data(existing_card, scryfall_data)
    
    # Display results
    print("📋 BEFORE MERGE (Existing Card):")
    print(f"  - Name: {existing_card['name']}")
    print(f"  - Analysis: {existing_card.get('analysis', 'None')[:50]}...")
    print(f"  - Priority: {existing_card.get('priority', 'None')}")
    print(f"  - Images: {len(existing_card.get('imageUris', {}))}")
    print(f"  - Prices: {len(existing_card.get('prices', {}))}")
    print(f"  - Legalities: {len(existing_card.get('legalities', {}))}")
    print(f"  - Artist: {existing_card.get('artist', 'Unknown')}")
    
    print("\n🔄 AFTER MERGE:")
    print(f"  - Name: {merged_card['name']}")
    print(f"  - Analysis: {merged_card.get('analysis', 'None')[:50]}..." if merged_card.get('analysis') else "  - Analysis: None")
    print(f"  - Priority: {merged_card.get('priority', 'None')}")
    print(f"  - Images: {len(merged_card.get('imageUris', {}))}")
    print(f"  - Prices: {len(merged_card.get('prices', {}))}")
    print(f"  - Legalities: {len(merged_card.get('legalities', {}))}")
    print(f"  - Artist: {merged_card.get('artist', 'Unknown')}")
    print(f"  - Scryfall ID: {merged_card.get('scryfallId', 'None')}")
    print(f"  - Enhanced At: {merged_card.get('enhancedAt', 'None')[:19]}")
    
    print("\n✅ PRESERVATION CHECK:")
    preserved_fields = ['analysis', 'analysisRequested', 'priority', 'requestCount', 'importedAt', '_id']
    for field in preserved_fields:
        if field in existing_card:
            preserved = merged_card.get(field) == existing_card.get(field)
            status = "✅" if preserved else "❌"
            print(f"  {status} {field}: {'Preserved' if preserved else 'Changed/Lost'}")
    
    print("\n🆕 ENHANCEMENTS ADDED:")
    new_fields = ['imageUris', 'prices', 'legalities', 'scryfallId', 'oracleId', 'enhancedAt']
    for field in new_fields:
        if field in merged_card and field not in existing_card:
            print(f"  ✨ {field}: Added")
    
    print(f"\n💾 FINAL MERGED CARD KEYS ({len(merged_card)} total):")
    for key in sorted(merged_card.keys()):
        print(f"    - {key}")

if __name__ == "__main__":
    test_intelligent_merge()
