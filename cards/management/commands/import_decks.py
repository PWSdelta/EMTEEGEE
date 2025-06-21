"""
Django management command to import MTG deck files.
Supports various deck formats including .dec, .txt, .mwDeck, and JSON formats.
Usage: python manage.py import_decks --path /path/to/deck/files/
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify
from cards.models import Card, Deck, DecklistItem
import os
import re
import json
from pathlib import Path
from datetime import datetime
import uuid


class Command(BaseCommand):
    help = 'Import MTG deck files from various formats'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            required=True,
            help='Path to directory containing deck files or single deck file'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['auto', 'mtgo', 'mtga', 'json', 'txt'],
            default='auto',
            help='Deck file format (auto-detect by default)'
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
            '--skip-missing-cards',
            action='store_true',
            help='Skip decks that contain cards not in the database'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        self.skip_missing_cards = options['skip_missing_cards']
        
        deck_path = Path(options['path'])
        
        if not deck_path.exists():
            raise CommandError(f'Path does not exist: {deck_path}')
        
        # Get list of deck files
        deck_files = []
        if deck_path.is_file():
            deck_files = [deck_path]
        elif deck_path.is_dir():
            # Find all deck files in directory
            extensions = ['.dec', '.txt', '.mwDeck', '.json', '.dck']
            for ext in extensions:
                deck_files.extend(deck_path.glob(f'**/*{ext}'))
        
        if not deck_files:
            raise CommandError(f'No deck files found in: {deck_path}')
        
        # Limit files if specified
        if options.get('limit'):
            deck_files = deck_files[:options['limit']]
        
        self.stdout.write(f'Found {len(deck_files)} deck files to import')
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for deck_file in deck_files:
            try:
                result = self.import_single_deck(deck_file, options['format'])
                if result == 'imported':
                    imported_count += 1
                elif result == 'skipped':
                    skipped_count += 1
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error importing {deck_file.name}: {e}')
                )
                if self.verbosity >= 2:
                    import traceback
                    traceback.print_exc()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Deck import complete: {imported_count} imported, '
                f'{skipped_count} skipped, {error_count} errors'
            )
        )
    
    def import_single_deck(self, deck_file, format_hint):
        """Import a single deck file."""
        
        if self.verbosity >= 2:
            self.stdout.write(f'Processing: {deck_file.name}')
        
        # Parse the deck file
        try:
            deck_data = self.parse_deck_file(deck_file, format_hint)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to parse {deck_file.name}: {e}')
            )
            return 'skipped'
        
        if not deck_data:
            return 'skipped'
        
        # Check if deck already exists
        if not self.dry_run:
            existing_deck = Deck.objects.filter(
                name=deck_data['name'],
                source=deck_data.get('source', 'imported')
            ).first()
            
            if existing_deck:
                if self.verbosity >= 2:
                    self.stdout.write(f'Deck already exists: {deck_data["name"]}')
                return 'skipped'
        
        # Validate cards exist in database
        missing_cards = []
        for card_entry in deck_data['cards']:
            card_name = card_entry['name']
            try:
                Card.objects.get(name__iexact=card_name)
            except Card.DoesNotExist:
                missing_cards.append(card_name)
        
        if missing_cards:
            if self.skip_missing_cards:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping {deck_data["name"]} - missing cards: {len(missing_cards)}'
                    )
                )
                return 'skipped'
            else:
                # Try to find cards with similar names
                for i, card_entry in enumerate(deck_data['cards']):
                    if card_entry['name'] in missing_cards:
                        similar_card = self.find_similar_card(card_entry['name'])
                        if similar_card:
                            deck_data['cards'][i]['name'] = similar_card.name
                            missing_cards.remove(card_entry['name'])
                
                if missing_cards:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {deck_data["name"]} - could not find cards: {missing_cards[:5]}'
                        )
                    )
                    return 'skipped'
        
        # Create the deck
        if not self.dry_run:
            deck = self.create_deck(deck_data)
            if self.verbosity >= 1:
                self.stdout.write(f'Imported deck: {deck.name} ({deck.total_cards} cards)')
        else:
            if self.verbosity >= 1:
                self.stdout.write(f'Would import: {deck_data["name"]} ({len(deck_data["cards"])} cards)')
        
        return 'imported'
    
    def parse_deck_file(self, deck_file, format_hint):
        """Parse a deck file and return structured data."""
        
        with open(deck_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Auto-detect format if needed
        if format_hint == 'auto':
            format_hint = self.detect_format(content, deck_file.suffix)
        
        if format_hint == 'json':
            return self.parse_json_deck(content, deck_file.stem)
        elif format_hint in ['mtgo', 'mtga', 'txt']:
            return self.parse_text_deck(content, deck_file.stem)
        else:
            return self.parse_text_deck(content, deck_file.stem)
    
    def detect_format(self, content, file_extension):
        """Auto-detect deck file format."""
        if file_extension.lower() == '.json':
            return 'json'
        elif 'Deck' in content and 'Sideboard' in content:
            return 'mtga'
        else:
            return 'txt'
    
    def parse_json_deck(self, content, filename):
        """Parse JSON format deck files."""
        try:
            data = json.loads(content)
            
            # Handle different JSON structures
            if 'mainboard' in data or 'sideboard' in data:
                return self.parse_moxfield_json(data, filename)
            elif 'deck' in data:
                return self.parse_generic_json(data, filename)
            else:
                return self.parse_simple_json(data, filename)
                
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON: {e}')
    
    def parse_text_deck(self, content, filename):
        """Parse text-based deck formats (MTGO, MTGA, etc.)."""
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        deck_data = {
            'name': filename.replace('_', ' ').title(),
            'format': 'unknown',
            'cards': [],
            'source': 'imported'
        }
        
        current_section = 'mainboard'
        
        for line in lines:
            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('#'):
                continue
            
            # Check for section headers
            if line.lower().startswith('sideboard'):
                current_section = 'sideboard'
                continue
            elif line.lower().startswith('maybeboard'):
                current_section = 'maybeboard'
                continue
            elif line.lower().startswith('commander'):
                current_section = 'commander'
                continue
            elif line.lower() in ['mainboard', 'main', 'deck']:
                current_section = 'mainboard'
                continue
            
            # Parse card line
            card_match = re.match(r'^(\d+)\s+(.+)$', line)
            if card_match:
                quantity = int(card_match.group(1))
                card_name = card_match.group(2).strip()
                
                # Clean up card name (remove set info, etc.)
                card_name = re.sub(r'\s+\([^)]+\)$', '', card_name)  # Remove (SET)
                card_name = re.sub(r'\s+\d+$', '', card_name)        # Remove collector number
                
                deck_data['cards'].append({
                    'name': card_name,
                    'quantity': quantity,
                    'location': current_section
                })
        
        # Try to detect format from card names or deck structure
        if any(card['location'] == 'commander' for card in deck_data['cards']):
            deck_data['format'] = 'commander'
        elif len([c for c in deck_data['cards'] if c['location'] == 'mainboard']) == 60:
            deck_data['format'] = 'standard'  # Could be modern, legacy, etc.
        
        return deck_data
    
    def parse_moxfield_json(self, data, filename):
        """Parse Moxfield-style JSON format."""
        deck_data = {
            'name': data.get('name', filename),
            'format': data.get('format', 'unknown'),
            'description': data.get('description', ''),
            'cards': [],
            'source': 'moxfield'
        }
        
        # Parse mainboard
        if 'mainboard' in data:
            for card_name, card_info in data['mainboard'].items():
                deck_data['cards'].append({
                    'name': card_name,
                    'quantity': card_info.get('quantity', 1),
                    'location': 'mainboard'
                })
        
        # Parse sideboard
        if 'sideboard' in data:
            for card_name, card_info in data['sideboard'].items():
                deck_data['cards'].append({
                    'name': card_name,
                    'quantity': card_info.get('quantity', 1),
                    'location': 'sideboard'
                })
        
        return deck_data
    
    def parse_generic_json(self, data, filename):
        """Parse generic JSON format."""
        # Implementation for other JSON formats
        return None
    
    def parse_simple_json(self, data, filename):
        """Parse simple JSON format."""
        # Implementation for simple JSON formats
        return None
    
    def find_similar_card(self, card_name):
        """Find a card with similar name in the database."""
        # Try exact match first (case insensitive)
        try:
            return Card.objects.get(name__iexact=card_name)
        except Card.DoesNotExist:
            pass
        
        # Try partial matches
        similar_cards = Card.objects.filter(name__icontains=card_name)
        if similar_cards.count() == 1:
            return similar_cards.first()
        
        # Try without special characters
        clean_name = re.sub(r'[^\w\s]', '', card_name)
        similar_cards = Card.objects.filter(name__icontains=clean_name)
        if similar_cards.count() == 1:
            return similar_cards.first()
        
        return None
    
    def create_deck(self, deck_data):
        """Create a deck from parsed data."""
        
        # Create the deck
        deck = Deck.objects.create(
            name=deck_data['name'],
            description=deck_data.get('description', ''),
            format=deck_data.get('format', 'other'),
            source=deck_data.get('source', 'imported'),
            total_cards=sum(card['quantity'] for card in deck_data['cards']),
            mainboard_count=sum(
                card['quantity'] for card in deck_data['cards'] 
                if card['location'] == 'mainboard'
            ),
            sideboard_count=sum(
                card['quantity'] for card in deck_data['cards'] 
                if card['location'] == 'sideboard'
            ),
        )
        
        # Add cards to deck
        for card_entry in deck_data['cards']:
            try:
                card = Card.objects.get(name__iexact=card_entry['name'])
                DeckCard.objects.create(
                    deck=deck,
                    card=card,
                    quantity=card_entry['quantity'],
                    location=card_entry['location']
                )
            except Card.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Card not found: {card_entry["name"]}')
                )
        
        # Calculate colors and other stats
        self.calculate_deck_stats(deck)
        
        return deck
    
    def calculate_deck_stats(self, deck):
        """Calculate deck statistics."""
        deck_cards = deck.deck_cards.select_related('card').all()
        
        # Calculate colors
        all_colors = set()
        total_cmc = 0
        total_cards = 0
        
        for deck_card in deck_cards:
            if deck_card.card.colors:
                all_colors.update(deck_card.card.colors)
            total_cmc += deck_card.card.cmc * deck_card.quantity
            total_cards += deck_card.quantity
        
        deck.colors = list(all_colors)
        deck.color_identity = list(all_colors)  # Simplified
        deck.avg_cmc = total_cmc / total_cards if total_cards > 0 else 0
        deck.save()
        
        # Create detailed stats
        stats, created = DeckStats.objects.get_or_create(deck=deck)
        
        # Calculate distributions
        cmc_dist = {}
        color_dist = {}
        type_dist = {}
        
        for deck_card in deck_cards:
            card = deck_card.card
            qty = deck_card.quantity
            
            # CMC distribution
            cmc = min(card.cmc, 7)  # Cap at 7+ for display
            cmc_key = f'{cmc}+' if cmc >= 7 else str(cmc)
            cmc_dist[cmc_key] = cmc_dist.get(cmc_key, 0) + qty
            
            # Color distribution
            for color in card.colors:
                color_dist[color] = color_dist.get(color, 0) + qty
            
            # Type distribution
            if 'Land' in card.type_line:
                type_dist['Land'] = type_dist.get('Land', 0) + qty
            elif 'Creature' in card.type_line:
                type_dist['Creature'] = type_dist.get('Creature', 0) + qty
            elif 'Instant' in card.type_line:
                type_dist['Instant'] = type_dist.get('Instant', 0) + qty
            elif 'Sorcery' in card.type_line:
                type_dist['Sorcery'] = type_dist.get('Sorcery', 0) + qty
            elif 'Artifact' in card.type_line:
                type_dist['Artifact'] = type_dist.get('Artifact', 0) + qty
            elif 'Enchantment' in card.type_line:
                type_dist['Enchantment'] = type_dist.get('Enchantment', 0) + qty
            elif 'Planeswalker' in card.type_line:
                type_dist['Planeswalker'] = type_dist.get('Planeswalker', 0) + qty
        
        stats.cmc_distribution = cmc_dist
        stats.color_distribution = color_dist
        stats.type_distribution = type_dist
        stats.lands_count = type_dist.get('Land', 0)
        stats.creatures_count = type_dist.get('Creature', 0)
        stats.spells_count = sum(
            type_dist.get(t, 0) for t in ['Instant', 'Sorcery']
        )
        stats.artifacts_count = type_dist.get('Artifact', 0)
        stats.save()
