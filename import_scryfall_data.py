#!/usr/bin/env python3
"""
Scryfall Bulk Data Importer for EMTEEGEE
Downloads and processes Scryfall's bulk card data to enhance our MongoDB collection.

INTELLIGENT MERGING APPROACH:
- For existing cards: Uses merge_card_data() to intelligently combine Scryfall data 
  with existing card data, preserving analysis results and user data
- For new cards: Creates full card records using process_card_data()
- NO "scryfall_" PREFIXING: Fields are merged directly into the card structure
- Rich data enhancement: Adds images, pricing, legalities, and other Scryfall-specific data
- Preserves important fields: analysis, analysisRequested, priority, etc. are never overwritten
"""

import requests
import json
import gzip
from pathlib import Path
from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional, Any
import os
import sys
from pymongo import UpdateOne, InsertOne

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scryfall_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScryfallBulkImporter:
    """Handles downloading and importing Scryfall bulk data."""
    
    BULK_DATA_API = "https://api.scryfall.com/bulk-data"
    DOWNLOAD_DIR = Path("downloads/scryfall")
    
    def __init__(self):
        self.download_dir = self.DOWNLOAD_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.cards_collection = get_cards_collection()
        
    def get_bulk_data_info(self) -> List[Dict[str, Any]]:
        """Fetch information about available bulk data files."""
        logger.info("Fetching bulk data information from Scryfall API...")
        
        try:
            response = requests.get(self.BULK_DATA_API, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            logger.error(f"Failed to fetch bulk data info: {e}")
            raise
    
    def find_dataset(self, dataset_type: str = "oracle_cards") -> Optional[Dict[str, Any]]:
        """Find a specific dataset by type."""
        bulk_data = self.get_bulk_data_info()
        
        for item in bulk_data:
            if item.get('type') == dataset_type:
                return item
        
        logger.error(f"Dataset type '{dataset_type}' not found!")
        return None
    
    def download_dataset(self, dataset_info: Dict[str, Any]) -> Path:
        """Download a bulk data file."""
        download_url = dataset_info['download_uri']
        filename = f"scryfall_{dataset_info['type']}_{dataset_info['updated_at'][:10]}.json"
        filepath = self.download_dir / filename
          # Check if already downloaded
        if filepath.exists():
            logger.info(f"Dataset already downloaded: {filepath}")
            return filepath
        
        logger.info(f"Downloading {dataset_info['name']} ({dataset_info['size'] / 1024 / 1024:.1f} MB)...")
        
        try:
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Check if data is actually gzipped by checking the content-type and first bytes
            is_gzipped = False
            first_chunk = None
            
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if first_chunk is None:
                        first_chunk = chunk
                        # Check if it's actually gzipped (starts with magic bytes)
                        is_gzipped = chunk.startswith(b'\x1f\x8b')
                    f.write(chunk)
            
            # If it was mistakenly marked as gzipped but isn't, we already saved the raw data correctly
            logger.info(f"Downloaded {'gzipped' if is_gzipped else 'uncompressed'} data")
            
            logger.info(f"Successfully downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            raise
    
    def merge_card_data(self, existing_card: Dict[str, Any], scryfall_card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently merge Scryfall data with existing card data.
        Preserves existing analysis and user data while enhancing with Scryfall info.
        """
        # Start with existing card data
        merged_card = existing_card.copy()
        
        # Core fields - enhance existing or add if missing
        field_mappings = {
            'name': 'name',
            'manaCost': 'mana_cost',
            'manaValue': 'cmc',
            'type': 'type_line',
            'text': 'oracle_text',
            'flavorText': 'flavor_text',
            'artist': 'artist',
            'collectorNumber': 'collector_number',
            'rarity': 'rarity',
            'setCode': 'set',
            'setName': 'set_name',
            'setType': 'set_type',
            'releasedAt': 'released_at',
            'colors': 'colors',
            'colorIdentity': 'color_identity',
            'keywords': 'keywords',
            'legalities': 'legalities',
            'layout': 'layout',
            'reserved': 'reserved',
            'digital': 'digital',
            'promo': 'promo',
            'reprint': 'reprint',
            'scryfallUri': 'scryfall_uri',
            'watermark': 'watermark',
            'scryfallId': 'id',
            'oracleId': 'oracle_id'
        }
        
        # Merge basic fields
        for our_field, scryfall_field in field_mappings.items():
            if scryfall_field in scryfall_card:
                scryfall_value = scryfall_card[scryfall_field]
                if scryfall_value is not None:
                    # Only override if we don't have the field or it's empty
                    if our_field not in merged_card or not merged_card[our_field]:
                        merged_card[our_field] = scryfall_value
                    elif our_field in ['keywords', 'colors', 'colorIdentity'] and isinstance(scryfall_value, list):
                        # For lists, merge and deduplicate
                        existing_list = merged_card.get(our_field, [])
                        if isinstance(existing_list, list):
                            merged_card[our_field] = list(set(existing_list + scryfall_value))
                        else:
                            merged_card[our_field] = scryfall_value
        
        # Handle creature stats
        for stat in ['power', 'toughness', 'loyalty']:
            if stat in scryfall_card and scryfall_card[stat] is not None:
                merged_card[stat] = scryfall_card[stat]
        
        # Handle multi-faced cards
        if 'card_faces' in scryfall_card:
            merged_card['cardFaces'] = scryfall_card['card_faces']
        
        # Always add/update rich Scryfall data
        merged_card.update({
            'imageUris': scryfall_card.get('image_uris', {}),
            'prices': scryfall_card.get('prices', {}),
            'purchaseUris': scryfall_card.get('purchase_uris', {}),
            
            # NEW: Card relationships and discovery
            'allParts': scryfall_card.get('all_parts', []),  # Related cards (tokens, meld, combos)
            'relatedUris': scryfall_card.get('related_uris', {}),  # External links
            
            # NEW: Competitive & meta data  
            'edhrecRank': scryfall_card.get('edhrec_rank'),
            'pennyRank': scryfall_card.get('penny_rank'),
            'gameChanger': scryfall_card.get('game_changer', False),
            
            # NEW: Physical card properties
            'borderColor': scryfall_card.get('border_color'),
            'frame': scryfall_card.get('frame'),
            'frameEffects': scryfall_card.get('frame_effects', []),
            'finishes': scryfall_card.get('finishes', []),
            'games': scryfall_card.get('games', []),
            'booster': scryfall_card.get('booster', False),
            'promoTypes': scryfall_card.get('promo_types', []),
            
            # NEW: Enhanced identification
            'multiverseIds': scryfall_card.get('multiverse_ids', []),
            'tcgplayerId': scryfall_card.get('tcgplayer_id'),
            'cardmarketId': scryfall_card.get('cardmarket_id'),
            'arenaId': scryfall_card.get('arena_id'),
            'mtgoId': scryfall_card.get('mtgo_id'),
            
            # NEW: Print quality & status
            'imageStatus': scryfall_card.get('image_status'),
            'highresImage': scryfall_card.get('highres_image', False),
            'contentWarning': scryfall_card.get('content_warning', False),
            
            'enhancedAt': datetime.now(timezone.utc).isoformat()
        })
        
        # Preserve important existing fields that shouldn't be overwritten
        preserve_fields = ['analysis', 'analysisRequested', 'analysisRequestedAt', 'analysisCompletedAt', 
                          'priority', 'requestCount', 'importedAt', 'uuid', '_id']
        
        for field in preserve_fields:
            if field in existing_card:
                merged_card[field] = existing_card[field]
        
        return merged_card

    def process_card_data(self, scryfall_card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single Scryfall card for new card creation.
        Creates a complete card structure from Scryfall data.
        """
        # Core card identification and basic info
        enhanced_card = {
            'name': scryfall_card.get('name'),
            'manaCost': scryfall_card.get('mana_cost', ''),
            'manaValue': scryfall_card.get('cmc', 0),
            'type': scryfall_card.get('type_line', ''),
            'text': scryfall_card.get('oracle_text', ''),
            'flavorText': scryfall_card.get('flavor_text'),
            'artist': scryfall_card.get('artist'),
            'collectorNumber': scryfall_card.get('collector_number'),
            'rarity': scryfall_card.get('rarity'),
            
            # Set information
            'setCode': scryfall_card.get('set'),
            'setName': scryfall_card.get('set_name'),
            'setType': scryfall_card.get('set_type'),
            'releasedAt': scryfall_card.get('released_at'),
            
            # Game mechanics
            'colors': scryfall_card.get('colors', []),
            'colorIdentity': scryfall_card.get('color_identity', []),
            'keywords': scryfall_card.get('keywords', []),
            'legalities': scryfall_card.get('legalities', {}),
            
            # Physical and digital availability
            'layout': scryfall_card.get('layout'),
            'reserved': scryfall_card.get('reserved', False),
            'digital': scryfall_card.get('digital', False),
            'promo': scryfall_card.get('promo', False),
            'reprint': scryfall_card.get('reprint', False),
            
            # URLs and references
            'scryfallUri': scryfall_card.get('scryfall_uri'),
            'watermark': scryfall_card.get('watermark'),
            
            # Scryfall-specific IDs for linking
            'scryfallId': scryfall_card.get('id'),
            'oracleId': scryfall_card.get('oracle_id'),
            
            # Rich media and pricing (new data)
            'imageUris': scryfall_card.get('image_uris', {}),
            'prices': scryfall_card.get('prices', {}),
            'purchaseUris': scryfall_card.get('purchase_uris', {}),
            
            # Card relationships and discovery
            'allParts': scryfall_card.get('all_parts', []),  # Related cards (tokens, meld, combos)
            'relatedUris': scryfall_card.get('related_uris', {}),  # External links
            
            # Competitive & meta data  
            'edhrecRank': scryfall_card.get('edhrec_rank'),
            'pennyRank': scryfall_card.get('penny_rank'),
            'gameChanger': scryfall_card.get('game_changer', False),
            
            # Physical card properties
            'borderColor': scryfall_card.get('border_color'),
            'frame': scryfall_card.get('frame'),
            'frameEffects': scryfall_card.get('frame_effects', []),
            'finishes': scryfall_card.get('finishes', []),
            'games': scryfall_card.get('games', []),
            'booster': scryfall_card.get('booster', False),
            'promoTypes': scryfall_card.get('promo_types', []),
            
            # Enhanced identification
            'multiverseIds': scryfall_card.get('multiverse_ids', []),
            'tcgplayerId': scryfall_card.get('tcgplayer_id'),
            'cardmarketId': scryfall_card.get('cardmarket_id'),
            'arenaId': scryfall_card.get('arena_id'),
            'mtgoId': scryfall_card.get('mtgo_id'),
            
            # Print quality & status
            'imageStatus': scryfall_card.get('image_status'),
            'highresImage': scryfall_card.get('highres_image', False),
            'contentWarning': scryfall_card.get('content_warning', False),
            
            # Update timestamp
            'enhancedAt': datetime.now(timezone.utc).isoformat()
        }
        
        # Handle creature stats
        if 'power' in scryfall_card:
            enhanced_card['power'] = scryfall_card['power']
        if 'toughness' in scryfall_card:
            enhanced_card['toughness'] = scryfall_card['toughness']
        if 'loyalty' in scryfall_card:
            enhanced_card['loyalty'] = scryfall_card['loyalty']
          # Handle multi-faced cards
        if 'card_faces' in scryfall_card:
            enhanced_card['cardFaces'] = scryfall_card['card_faces']        # Remove None values to keep the document clean
        enhanced_card = {k: v for k, v in enhanced_card.items() if v is not None}
        
        return enhanced_card

    def import_cards_batch(self, cards_data: List[Dict[str, Any]], batch_size: int = 2357) -> Dict[str, int]:
        """Import cards in batches to MongoDB with highly optimized bulk operations."""
        stats = {'updated': 0, 'new': 0, 'errors': 0}
        
        for i in range(0, len(cards_data), batch_size):
            batch = cards_data[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(cards_data) + batch_size - 1) // batch_size
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} cards)")
            
            # Pre-process all names and IDs for batch lookup
            batch_names = []
            batch_ids = []
            for card in batch:
                if card.get('name'):
                    batch_names.append(card['name'])
                if card.get('id'):
                    batch_ids.append(card['id'])
            
            # Single optimized query to find all existing cards
            existing_cards_map = {}
            if batch_names or batch_ids:
                query_filters = []
                if batch_names:
                    query_filters.append({'name': {'$in': batch_names}})
                if batch_ids:
                    query_filters.append({'scryfallId': {'$in': batch_ids}})
                    query_filters.append({'uuid': {'$in': batch_ids}})
                
                existing_cursor = self.cards_collection.find(
                    {'$or': query_filters},
                    {'name': 1, 'scryfallId': 1, 'uuid': 1, 'analysis': 1, 'analysisRequested': 1, 'priority': 1}
                )
                
                # Build lookup map
                for existing in existing_cursor:
                    if 'name' in existing:
                        existing_cards_map[existing['name']] = existing
                    if 'scryfallId' in existing:
                        existing_cards_map[existing['scryfallId']] = existing
                    if 'uuid' in existing:
                        existing_cards_map[existing['uuid']] = existing
            
            # Prepare bulk operations with minimal processing
            bulk_operations = []
            timestamp = datetime.now(timezone.utc).isoformat()
            
            for scryfall_card in batch:
                try:
                    card_name = scryfall_card.get('name')
                    card_id = scryfall_card.get('id')
                    
                    # Quick lookup
                    existing_card = existing_cards_map.get(card_name) or existing_cards_map.get(card_id)
                    
                    if existing_card:
                        # Fast update with essential Scryfall data only
                        update_doc = {
                            'scryfallId': card_id,
                            'oracleId': scryfall_card.get('oracle_id'),
                            'manaCost': scryfall_card.get('mana_cost', ''),
                            'manaValue': scryfall_card.get('cmc', 0),
                            'type': scryfall_card.get('type_line', ''),
                            'text': scryfall_card.get('oracle_text', ''),
                            'rarity': scryfall_card.get('rarity'),
                            'setCode': scryfall_card.get('set'),
                            'colors': scryfall_card.get('colors', []),
                            'colorIdentity': scryfall_card.get('color_identity', []),
                            'legalities': scryfall_card.get('legalities', {}),
                            'edhrecRank': scryfall_card.get('edhrec_rank'),
                            'prices': scryfall_card.get('prices', {}),
                            'imageUris': scryfall_card.get('image_uris', {}),
                            'allParts': scryfall_card.get('all_parts', []),
                            'enhancedAt': timestamp
                        }
                        
                        # Add creature stats if present
                        for stat in ['power', 'toughness', 'loyalty']:
                            if stat in scryfall_card:
                                update_doc[stat] = scryfall_card[stat]
                        
                        # Remove None values
                        update_doc = {k: v for k, v in update_doc.items() if v is not None}
                        
                        bulk_operations.append(UpdateOne(
                            {'_id': existing_card['_id']},
                            {'$set': update_doc}
                        ))
                        stats['updated'] += 1
                    else:
                        # Fast new card creation
                        new_card = {
                            'name': card_name,
                            'uuid': card_id,
                            'scryfallId': card_id,
                            'oracleId': scryfall_card.get('oracle_id'),
                            'manaCost': scryfall_card.get('mana_cost', ''),
                            'manaValue': scryfall_card.get('cmc', 0),
                            'type': scryfall_card.get('type_line', ''),
                            'text': scryfall_card.get('oracle_text', ''),
                            'rarity': scryfall_card.get('rarity'),
                            'setCode': scryfall_card.get('set'),
                            'setName': scryfall_card.get('set_name'),
                            'colors': scryfall_card.get('colors', []),
                            'colorIdentity': scryfall_card.get('color_identity', []),
                            'legalities': scryfall_card.get('legalities', {}),
                            'edhrecRank': scryfall_card.get('edhrec_rank'),
                            'prices': scryfall_card.get('prices', {}),
                            'imageUris': scryfall_card.get('image_uris', {}),
                            'allParts': scryfall_card.get('all_parts', []),
                            'importedAt': timestamp,
                            'enhancedAt': timestamp
                        }
                        
                        # Add creature stats if present
                        for stat in ['power', 'toughness', 'loyalty']:
                            if stat in scryfall_card:
                                new_card[stat] = scryfall_card[stat]
                        
                        # Remove None values
                        new_card = {k: v for k, v in new_card.items() if v is not None}
                        
                        bulk_operations.append(InsertOne(new_card))
                        stats['new'] += 1
                
                except Exception as e:
                    logger.error(f"Error processing card {scryfall_card.get('name', 'Unknown')}: {e}")
                    stats['errors'] += 1
            
            # Execute bulk operations
            if bulk_operations:
                try:
                    logger.info(f"Executing {len(bulk_operations)} bulk operations for batch {batch_num}")
                    result = self.cards_collection.bulk_write(bulk_operations, ordered=False)
                    logger.info(f"Batch {batch_num} completed: {result.upserted_count} inserted, {result.modified_count} updated")
                except Exception as e:
                    logger.error(f"Bulk operation failed for batch {batch_num}: {e}")
                    stats['errors'] += len(bulk_operations)
                    # Reset the successful stats since bulk operation failed
                    stats['updated'] -= sum(1 for op in bulk_operations if isinstance(op, UpdateOne))
                    stats['new'] -= sum(1 for op in bulk_operations if isinstance(op, InsertOne))
            
        return stats
    
    def import_dataset(self, dataset_type: str = "oracle_cards") -> Dict[str, int]:
        """Main method to import a Scryfall dataset."""
        logger.info(f"Starting import of {dataset_type} dataset...")
        
        # Get dataset info
        dataset_info = self.find_dataset(dataset_type)
        if not dataset_info:
            raise ValueError(f"Dataset {dataset_type} not found")
        
        # Download dataset
        filepath = self.download_dataset(dataset_info)
        
        # Load and process the JSON data
        logger.info("Loading JSON data...")
        with open(filepath, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
        
        logger.info(f"Loaded {len(cards_data)} cards from Scryfall")
        
        # Import the data
        stats = self.import_cards_batch(cards_data)
        
        logger.info(f"Import completed: {stats}")
        return stats

def main():
    """Main function to run the import."""
    importer = ScryfallBulkImporter()
    
    try:
        # Import the oracle cards dataset (unique cards only, ~34k)
        stats = importer.import_dataset("oracle_cards")
        
        print("\n" + "="*50)
        print("SCRYFALL ORACLE CARDS IMPORT COMPLETED")
        print("="*50)
        print(f"Updated existing cards: {stats['updated']}")
        print(f"New cards added: {stats['new']}")
        print(f"Errors: {stats['errors']}")
        print(f"Total processed: {sum(stats.values())}")
        print("\n💡 Oracle Cards contains unique card identities (~34k)")
        print("   Perfect for analysis - no duplicate printings!")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise

if __name__ == "__main__":
    main()
