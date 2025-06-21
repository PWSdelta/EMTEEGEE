"""
Django management command to import Scryfall bulk data.
Usage: python manage.py import_scryfall_data [--dataset=default_cards]
"""

from django.core.management.base import BaseCommand, CommandError
import sys
import os

# Add the project root to import our custom script
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from import_scryfall_data import ScryfallBulkImporter
except ImportError:
    # If requests isn't installed, provide helpful error
    raise ImportError(
        "Missing required packages. Please install: pip install requests"
    )

class Command(BaseCommand):
    help = 'Import card data from Scryfall bulk data API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            default='default_cards',
            choices=['oracle_cards', 'unique_artwork', 'default_cards', 'all_cards'],
            help='Type of dataset to import (default: default_cards)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of cards to process in each batch (default: 1000)'
        )

    def handle(self, *args, **options):
        dataset_type = options['dataset']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting Scryfall import: {dataset_type}')
        )
        
        try:
            importer = ScryfallBulkImporter()
            stats = importer.import_dataset(dataset_type)
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write(
                self.style.SUCCESS('SCRYFALL IMPORT COMPLETED SUCCESSFULLY')
            )
            self.stdout.write("="*60)
            self.stdout.write(f"Updated existing cards: {stats['updated']}")
            self.stdout.write(f"New cards added: {stats['new']}")
            self.stdout.write(f"Errors encountered: {stats['errors']}")
            self.stdout.write(f"Total cards processed: {sum(stats.values())}")
            
            if stats['errors'] > 0:
                self.stdout.write(
                    self.style.WARNING(f"Check scryfall_import.log for error details")
                )
            
        except Exception as e:
            raise CommandError(f'Import failed: {str(e)}')
