"""
Management command to clear all analysis components from cards.
"""

from django.core.management.base import BaseCommand
from cards.models import get_cards_collection

class Command(BaseCommand):
    help = 'Clear all analysis components from cards'
    
    def handle(self, *args, **options):
        cards_collection = get_cards_collection()
        
        # Clear components
        result = cards_collection.update_many(
            {'analysis.components': {'$exists': True}},
            {'$unset': {'analysis.components': ''}}
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Cleared components from {result.modified_count} cards')
        )
        
        # Also clear counts and flags
        result2 = cards_collection.update_many(
            {'analysis.component_count': {'$exists': True}},
            {'$unset': {'analysis.component_count': '', 'analysis.fully_analyzed': ''}}
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Cleared analysis flags from {result2.modified_count} cards')
        )
