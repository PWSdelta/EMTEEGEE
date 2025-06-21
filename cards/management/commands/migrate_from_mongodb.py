"""
Django management command to migrate cards from MongoDB to Django models.
Usage: python manage.py migrate_from_mongodb
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cards.models import Card
from analyses.models import AnalysisComponent, PriceHistory
import uuid
from decimal import Decimal

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class Command(BaseCommand):
    help = 'Migrate card data from MongoDB to Django models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mongo-url',
            type=str,
            default='mongodb://localhost:27017/',
            help='MongoDB connection URL'
        )
        parser.add_argument(
            '--database',
            type=str,
            default='MagicAI',
            help='MongoDB database name'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually saving data'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of cards to migrate (for testing)'
        )
    
    def handle(self, *args, **options):
        if not PYMONGO_AVAILABLE:
            raise CommandError(
                'pymongo is required for this command. Install it with: pip install pymongo'
            )
        
        self.dry_run = options['dry_run']
        self.verbosity = options['verbosity']
        
        # Connect to MongoDB
        try:
            mongo_client = MongoClient(options['mongo_url'])
            mongo_db = mongo_client[options['database']]
            
            # Test connection
            mongo_db.list_collection_names()
            self.stdout.write(
                self.style.SUCCESS(f'Connected to MongoDB: {options["database"]}')
            )
        except Exception as e:
            raise CommandError(f'Failed to connect to MongoDB: {e}')
        
        # Migrate cards
        self.migrate_cards(mongo_db, options.get('limit'))
        
        # Migrate analysis components
        self.migrate_analysis_components(mongo_db)
        
        self.stdout.write(
            self.style.SUCCESS('Migration completed successfully!')
        )
    
    def migrate_cards(self, mongo_db, limit=None):
        """Migrate cards from MongoDB cards collection to Django Card model."""
        cards_collection = mongo_db.cards
        
        # Get total count
        total_cards = cards_collection.count_documents({})
        if limit:
            total_cards = min(total_cards, limit)
        
        self.stdout.write(f'Migrating {total_cards} cards...')
        
        # Query cards
        cursor = cards_collection.find({})
        if limit:
            cursor = cursor.limit(limit)
        
        migrated_count = 0
        skipped_count = 0
        
        for mongo_card in cursor:
            try:
                # Check if card already exists
                scryfall_id = mongo_card.get('id')
                if not scryfall_id:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping card without scryfall_id: {mongo_card.get("name", "Unknown")}')
                    )
                    skipped_count += 1
                    continue
                
                # Convert string UUID to UUID object if needed
                if isinstance(scryfall_id, str):
                    try:
                        scryfall_id = uuid.UUID(scryfall_id)
                    except ValueError:
                        self.stdout.write(
                            self.style.WARNING(f'Invalid UUID format: {scryfall_id}')
                        )
                        skipped_count += 1
                        continue
                
                if not self.dry_run:
                    card, created = Card.objects.get_or_create(
                        scryfall_id=scryfall_id,
                        defaults={
                            'name': mongo_card.get('name', ''),
                            'mana_cost': mongo_card.get('mana_cost', ''),
                            'cmc': mongo_card.get('cmc', 0),
                            'type_line': mongo_card.get('type_line', ''),
                            'oracle_text': mongo_card.get('oracle_text', ''),
                            'colors': mongo_card.get('colors', []),
                            'color_identity': mongo_card.get('color_identity', []),
                            'power': mongo_card.get('power', ''),
                            'toughness': mongo_card.get('toughness', ''),
                            'rarity': mongo_card.get('rarity', 'common'),
                            'set_code': mongo_card.get('set', ''),
                            'collector_number': mongo_card.get('collector_number', ''),
                            'image_uris': mongo_card.get('image_uris', {}),
                            'prices': mongo_card.get('prices', {}),
                            'legalities': mongo_card.get('legalities', {}),
                            'fully_analyzed': mongo_card.get('fully_analyzed', False),
                            'analysis_completed_at': mongo_card.get('analysis_completed_at'),
                            'component_count': mongo_card.get('component_count', 0),
                        }
                    )
                    
                    if created:
                        migrated_count += 1
                        if self.verbosity >= 2:
                            self.stdout.write(f'Created card: {card.name}')
                    else:
                        if self.verbosity >= 2:
                            self.stdout.write(f'Card already exists: {card.name}')
                else:
                    # Dry run
                    migrated_count += 1
                    if self.verbosity >= 2:
                        self.stdout.write(f'Would create card: {mongo_card.get("name", "Unknown")}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error migrating card {mongo_card.get("name", "Unknown")}: {e}')
                )
                skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Cards migration: {migrated_count} migrated, {skipped_count} skipped')
        )
    
    def migrate_analysis_components(self, mongo_db):
        """Migrate analysis components from MongoDB to Django model."""
        components_collection = mongo_db.review_components
        
        total_components = components_collection.count_documents({})
        self.stdout.write(f'Migrating {total_components} analysis components...')
        
        migrated_count = 0
        skipped_count = 0
        
        for mongo_component in components_collection.find({}):
            try:
                # Find the corresponding card
                card_id = mongo_component.get('card_id')
                if not card_id:
                    skipped_count += 1
                    continue
                
                # card_id in MongoDB might be ObjectId or UUID string
                # We need to match it to our Django Card model
                try:
                    if isinstance(card_id, str):
                        # Try as UUID first
                        try:
                            card = Card.objects.get(scryfall_id=uuid.UUID(card_id))
                        except (ValueError, Card.DoesNotExist):
                            # If that fails, skip for now
                            # In a real migration, you'd need to handle ObjectId references
                            skipped_count += 1
                            continue
                    else:
                        # Handle ObjectId case - this would need custom logic
                        skipped_count += 1
                        continue
                except Card.DoesNotExist:
                    skipped_count += 1
                    continue
                
                if not self.dry_run:
                    component, created = AnalysisComponent.objects.get_or_create(
                        card=card,
                        component_type=mongo_component.get('component_type', 'thematic_analysis'),
                        defaults={
                            'content_markdown': mongo_component.get('content_markdown', ''),
                            'content_html': mongo_component.get('content_html', ''),
                            'model_used': mongo_component.get('model_used', 'unknown'),
                            'generation_metadata': mongo_component.get('generation_metadata', {}),
                            'is_active': mongo_component.get('is_active', True),
                        }
                    )
                    
                    if created:
                        migrated_count += 1
                        if self.verbosity >= 2:
                            self.stdout.write(f'Created component: {card.name} - {component.component_type}')
                else:
                    # Dry run
                    migrated_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error migrating component: {e}')
                )
                skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Components migration: {migrated_count} migrated, {skipped_count} skipped')
        )
