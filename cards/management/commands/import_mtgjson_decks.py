"""
Django management command to import MTGJson deck files directly to MongoDB.
Downloads and imports deck JSON files from MTGJson format.
Usage: python manage.py import_decks --path /path/to/mtgjson/deck/files/
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cards.models import Card, Deck
import os
import json
from pathlib import Path
from datetime import datetime
import requests
from pymongo import MongoClient
from django.conf import settings


class Command(BaseCommand):
    help = 'Import MTGJson deck files directly to MongoDB'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to directory containing MTGJson deck files'
        )
        parser.add_argument(
            '--url',
            type=str,
            help='Download deck files from MTGJson URL'
        )
        parser.add_argument(
            '--decklist',
            type=str,
            default='downloads/decklist.json',
            help='Path to MTGJson decklist.json metadata file'
        )
        parser.add_argument(
            '--download-from-decklist',
            action='store_true',
            help='Download decks listed in decklist.json metadata'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually saving data'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of decks to import (for testing)'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing decks if they already exist'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        self.update_existing = options['update_existing']
          # Get MongoDB connection
        self.mongo_client = self.get_mongo_client()
        self.db = self.mongo_client[settings.MONGODB_SETTINGS['db_name']]
        
        deck_files = []
          # Download from decklist if specified
        if options.get('download_from_decklist'):
            deck_files = self.download_from_decklist(options['decklist'], options.get('limit'))
        elif options.get('url'):
            deck_files = self.download_deck_files(options['url'])
        elif options.get('path'):
            deck_path = Path(options['path'])
            if not deck_path.exists():
                raise CommandError(f'Path does not exist: {deck_path}')
            
            if deck_path.is_file():
                deck_files = [deck_path]
            elif deck_path.is_dir():
                deck_files = list(deck_path.glob('**/*.json'))
        else:
            raise CommandError('Either --path or --url must be specified')
        
        if not deck_files:
            raise CommandError('No deck files found')
        
        # Limit files if specified
        if options.get('limit'):
            deck_files = deck_files[:options['limit']]
        
        self.stdout.write(f'Found {len(deck_files)} deck files to import')
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for deck_file in deck_files:
            try:
                result = self.import_single_deck_file(deck_file)
                if result == 'imported':
                    imported_count += 1
                elif result == 'updated':
                    updated_count += 1
                elif result == 'skipped':
                    skipped_count += 1
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error importing {deck_file}: {e}')
                )
                if self.verbosity >= 2:
                    import traceback
                    traceback.print_exc()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Deck import complete: {imported_count} imported, '                f'{updated_count} updated, {skipped_count} skipped, {error_count} errors'
            )
        )
    
    def get_mongo_client(self):
        """Get MongoDB client from Django settings."""
        mongodb_settings = settings.MONGODB_SETTINGS
        
        # Create connection string
        if mongodb_settings['username'] and mongodb_settings['password']:
            return MongoClient(
                host=mongodb_settings['host'],
                username=mongodb_settings['username'],
                password=mongodb_settings['password'],
                authSource=mongodb_settings['auth_source']
            )
        else:
            return MongoClient(mongodb_settings['host'])
    
    def download_from_decklist(self, decklist_path, limit=None):
        """Download deck files based on decklist.json metadata."""
        decklist_file = Path(decklist_path)
        if not decklist_file.exists():
            raise CommandError(f'Decklist file not found: {decklist_path}')
        
        # Load decklist metadata
        with open(decklist_file, 'r', encoding='utf-8') as f:
            decklist_data = json.load(f)
        
        self.stdout.write(f'Found {len(decklist_data)} decks in decklist')
        
        # Limit if specified
        deck_items = list(decklist_data.items())
        if limit:
            deck_items = deck_items[:limit]
        
        downloaded_files = []
        downloads_dir = Path('downloads/deck_files')
        downloads_dir.mkdir(exist_ok=True)
        
        for deck_code, deck_metadata in deck_items:
            # Download individual deck file
            deck_url = f"https://mtgjson.com/api/v5/decks/{deck_code}.json"
            deck_file = downloads_dir / f"{deck_code}.json"
            
            if deck_file.exists() and not self.update_existing:
                if self.verbosity >= 2:
                    self.stdout.write(f'Deck file already exists: {deck_file}')
                downloaded_files.append(deck_file)
                continue
            
            try:
                response = requests.get(deck_url)
                response.raise_for_status()
                
                with open(deck_file, 'wb') as f:
                    f.write(response.content)
                
                downloaded_files.append(deck_file)
                if self.verbosity >= 1:
                    self.stdout.write(f'Downloaded: {deck_code}.json')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to download {deck_code}: {e}')
                )
        
        return downloaded_files

    def download_deck_files(self, url):
        """Download deck files from MTGJson."""
        # This would implement downloading from MTGJson
        # For now, return empty list
        self.stdout.write('Downloading from URL not implemented yet')
        return []
    
    def import_single_deck_file(self, deck_file):
        """Import a single MTGJson deck file."""
        
        if self.verbosity >= 2:
            self.stdout.write(f'Processing: {deck_file}')
        
        # Read and parse the JSON file
        try:
            with open(deck_file, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to parse {deck_file}: {e}')
            )
            return 'skipped'
        
        # MTGJson deck files have a "data" key containing deck objects
        if 'data' not in deck_data:
            self.stdout.write(
                self.style.WARNING(f'No "data" key found in {deck_file}')
            )
            return 'skipped'
        
        imported_decks = 0
        
        # Process each deck in the file
        for deck_name, deck_info in deck_data['data'].items():
            try:
                result = self.import_single_deck(deck_name, deck_info)
                if result in ['imported', 'updated']:
                    imported_decks += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing deck {deck_name}: {e}')
                )        
        if imported_decks > 0:
            return 'imported'
        else:
            return 'skipped'
    
    def import_single_deck(self, deck_name, deck_data):
        """Import a single deck from MTGJson format."""
        
        # Use the deck code as the unique identifier, fallback to name
        deck_code = deck_data.get('code', deck_name)
        
        # Check if deck already exists
        existing_deck = self.db.decks.find_one({'code': deck_code})
        
        if existing_deck and not self.update_existing:
            if self.verbosity >= 2:
                self.stdout.write(f'Deck already exists: {deck_name} ({deck_code})')
            return 'skipped'
        
        # Prepare deck document for MongoDB (preserving MTGJson structure)
        deck_doc = {
            'code': deck_code,
            'name': deck_data.get('name', deck_name),
            'type': deck_data.get('type', 'deck'),
            'releaseDate': deck_data.get('releaseDate'),
            'sealedProductUuids': deck_data.get('sealedProductUuids', ''),
            
            # Card lists (preserving MTGJson CardDeck structure)
            'mainBoard': deck_data.get('mainBoard', []),
            'sideBoard': deck_data.get('sideBoard', []),
            'commander': deck_data.get('commander', []),
            
            # Calculate total cards for easy reference
            'totalCards': (
                len(deck_data.get('mainBoard', [])) +
                len(deck_data.get('sideBoard', [])) +
                len(deck_data.get('commander', []))
            ),
            
            # MagicAI analysis fields
            'fully_analyzed': False,
            'analysis_completed_at': None,
            
            # Timestamps
            'imported_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        # Validate that cards in deck exist in our cards collection
        self.validate_deck_cards(deck_doc)
        
        if not self.dry_run:
            if existing_deck:
                # Update existing deck
                self.db.decks.update_one(
                    {'code': deck_code},
                    {'$set': deck_doc}
                )
                if self.verbosity >= 1:
                    self.stdout.write(f'Updated deck: {deck_name} ({deck_code})')
                return 'updated'
            else:
                # Insert new deck
                self.db.decks.insert_one(deck_doc)
                if self.verbosity >= 1:                    self.stdout.write(f'Imported deck: {deck_name} ({deck_code})')
                return 'imported'
        else:
            if self.verbosity >= 1:
                self.stdout.write(f'Would import deck: {deck_name} ({deck_code})')
            return 'imported'
    
    def validate_deck_cards(self, deck_doc):
        """Validate that all cards in the deck exist in our cards collection."""
        missing_cards = []
        
        # Check all card sections
        for section in ['mainBoard', 'sideBoard', 'commander']:
            for card_entry in deck_doc.get(section, []):
                # MTGJson CardDeck format has 'uuid' field
                card_uuid = card_entry.get('uuid')
                card_name = card_entry.get('name', 'Unknown')
                
                if card_uuid:
                    # Check if card exists in our cards collection
                    card_exists = self.db.cards.find_one({'uuid': card_uuid})
                    if not card_exists:
                        missing_cards.append(f"{card_name} ({card_uuid[:8]}...)")
                else:
                    missing_cards.append(f"{card_name} (no UUID)")
        
        if missing_cards and self.verbosity >= 2:
            self.stdout.write(
                self.style.WARNING(
                    f'Missing cards in deck {deck_doc["name"]}: {", ".join(missing_cards[:5])}'
                    + (f' and {len(missing_cards) - 5} more' if len(missing_cards) > 5 else '')
                )
            )
    
    def parse_date(self, date_string):
        """Parse date string from MTGJson format."""
        if not date_string:
            return None
        
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
