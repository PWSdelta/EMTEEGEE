"""
Django management command to import MTGJson AtomicCards data.
Downloads and imports card data from MTGJson AtomicCards.json format.
Usage: python manage.py import_atomic_cards --url https://mtgjson.com/api/v5/AtomicCards.json
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cards.models import Card
import json
import requests
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from django.conf import settings
import uuid


class Command(BaseCommand):
    help = 'Import MTGJson AtomicCards data to MongoDB'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://mtgjson.com/api/v5/AtomicCards.json',
            help='URL to download AtomicCards.json from MTGJson'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Local path to AtomicCards.json file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually saving data'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of cards to import (for testing)'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing cards if they already exist'
        )
        parser.add_argument(
            '--download-only',
            action='store_true',
            help='Only download the file, do not import'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        self.update_existing = options['update_existing']
          # Get MongoDB connection
        self.mongo_client = self.get_mongo_client()
        self.db = self.mongo_client[settings.MONGODB_SETTINGS['db_name']]
        
        # Get the data
        if options.get('file'):
            card_data = self.load_from_file(options['file'])
        else:
            card_data = self.download_and_load(options['url'], options.get('download_only', False))
        
        if not card_data:
            raise CommandError('No card data loaded')
        
        if options.get('download_only'):
            self.stdout.write(self.style.SUCCESS('Download complete!'))
            return        
        # Import the cards
        self.import_cards(card_data, options.get('limit'))
    
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
    
    def download_and_load(self, url, download_only=False):
        """Download AtomicCards.json from MTGJson."""
        
        self.stdout.write(f'Downloading AtomicCards from: {url}')
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
              # Save to downloads directory
            downloads_dir = Path('downloads')
            downloads_dir.mkdir(exist_ok=True)
            filename = 'AtomicCards.json'
            filepath = downloads_dir / filename
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and self.verbosity >= 1:
                            percent = (downloaded / total_size) * 100
                            self.stdout.write(f'\rDownloaded: {percent:.1f}%', ending='')
            
            if self.verbosity >= 1:
                self.stdout.write(f'\nDownload complete: {filepath}')
            
            if download_only:
                return None
            
            # Load and return the data
            return self.load_from_file(filepath)
            
        except requests.RequestException as e:
            raise CommandError(f'Failed to download: {e}')
    
    def load_from_file(self, filepath):
        """Load AtomicCards data from local JSON file."""
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise CommandError(f'File does not exist: {filepath}')
        
        self.stdout.write(f'Loading card data from: {filepath}')
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'data' not in data:
                raise CommandError('Invalid AtomicCards format: missing "data" key')
            
            card_count = len(data['data'])
            self.stdout.write(f'Loaded {card_count:,} cards from file')
            
            return data['data']
            
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {e}')
        except Exception as e:
            raise CommandError(f'Error loading file: {e}')
    
    def import_cards(self, card_data, limit=None):
        """Import cards to MongoDB."""
        
        self.stdout.write('Starting card import...')
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each card
        card_names = list(card_data.keys())
        if limit:
            card_names = card_names[:limit]
        
        total_cards = len(card_names)
        
        for i, card_name in enumerate(card_names):
            if self.verbosity >= 2 and i % 1000 == 0:
                self.stdout.write(f'Processing card {i+1:,} of {total_cards:,}: {card_name}')
            
            card_variations = card_data[card_name]
            
            # Process each variation of the card
            for card_info in card_variations:
                try:
                    result = self.import_single_card(card_name, card_info)
                    if result == 'imported':
                        imported_count += 1
                    elif result == 'updated':
                        updated_count += 1
                    elif result == 'skipped':
                        skipped_count += 1
                        
                except Exception as e:
                    error_count += 1
                    if self.verbosity >= 2:
                        self.stdout.write(
                            self.style.ERROR(f'Error importing {card_name}: {e}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Card import complete: {imported_count:,} imported, '
                f'{updated_count:,} updated, {skipped_count:,} skipped, {error_count:,} errors'
            )
        )
    
    def import_single_card(self, card_name, card_data):
        """Import a single card from MTGJson AtomicCards format."""
        
        # Generate or use existing UUID
        card_uuid = card_data.get('uuid')
        if not card_uuid:
            # Generate UUID if not provided
            card_uuid = str(uuid.uuid4())
        
        # Check if card already exists
        existing_card = self.db.cards.find_one({'uuid': card_uuid})
        
        if existing_card and not self.update_existing:
            return 'skipped'
        
        # Prepare card document for MongoDB (MTGJson format)
        card_doc = {
            'uuid': card_uuid,
            'name': card_name,
            'manaCost': card_data.get('manaCost', ''),
            'manaValue': card_data.get('manaValue', 0),
            'type': card_data.get('type', ''),
            'text': card_data.get('text', ''),
            'colors': card_data.get('colors', []),
            'colorIdentity': card_data.get('colorIdentity', []),
            'power': card_data.get('power', ''),
            'toughness': card_data.get('toughness', ''),
            'rarity': card_data.get('rarity', ''),
            'setCode': card_data.get('setCode', ''),
            'number': card_data.get('number', ''),
            'artist': card_data.get('artist', ''),
            'flavorText': card_data.get('flavorText', ''),
            'layout': card_data.get('layout', ''),
            'side': card_data.get('side', ''),
            
            # Additional MTGJson fields
            'subtypes': card_data.get('subtypes', []),
            'supertypes': card_data.get('supertypes', []),
            'types': card_data.get('types', []),
            'keywords': card_data.get('keywords', []),
            'loyalty': card_data.get('loyalty', ''),
            'defense': card_data.get('defense', ''),
            
            # Legalities
            'legalities': card_data.get('legalities', {}),
            
            # Analysis status (our custom fields)
            'fully_analyzed': False,
            'analysis_completed_at': None,
            'component_count': 0,
            
            # Timestamps
            'imported_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        if not self.dry_run:
            if existing_card:
                # Update existing card
                self.db.cards.update_one(
                    {'uuid': card_uuid},
                    {'$set': card_doc}
                )
                if self.verbosity >= 3:
                    self.stdout.write(f'Updated card: {card_name}')
                return 'updated'
            else:
                # Insert new card
                self.db.cards.insert_one(card_doc)
                if self.verbosity >= 3:
                    self.stdout.write(f'Imported card: {card_name}')
                return 'imported'
        else:
            if self.verbosity >= 3:
                self.stdout.write(f'Would import card: {card_name}')
            return 'imported'
