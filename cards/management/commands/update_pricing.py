"""
Django management command to update card pricing with MTGjson data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from cards.pricing_manager import get_pricing_manager
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update card pricing with comprehensive MTGjson data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-history',
            action='store_true',
            help='Skip downloading 90-day price history (faster)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Download and process data without updating database',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏷️ Starting MTG Pricing Update...')
        )

        try:
            pricing_manager = get_pricing_manager()
            
            # Run full pricing update
            include_history = not options['skip_history']
            
            if options['dry_run']:
                self.stdout.write('📊 Dry run mode - will not update database')
                
                # Download and process data only
                pricing_data = pricing_manager.download_mtgjson_pricing(include_history=include_history)
                card_prices = pricing_manager.extract_card_pricing(pricing_data)
                card_prices = pricing_manager.calculate_price_metrics(card_prices)
                card_prices = pricing_manager.merge_with_scryfall_pricing(card_prices)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Processed pricing for {len(card_prices)} cards (dry run)')
                )
                
                # Show sample data
                if card_prices:
                    sample_uuid = list(card_prices.keys())[0]
                    sample_data = card_prices[sample_uuid]
                    
                    self.stdout.write('\n📋 Sample pricing data:')
                    self.stdout.write(f'Card UUID: {sample_uuid}')
                    
                    if 'merged_pricing' in sample_data:
                        pricing = sample_data['merged_pricing']
                        self.stdout.write(f'USD Price: ${pricing.get("usd", 0):.2f}')
                        self.stdout.write(f'EUR Price: €{pricing.get("eur", 0):.2f}')
                        self.stdout.write(f'Trend (30d): {pricing.get("price_trend_30d", 0):.1f}%')
                        self.stdout.write(f'Sources: {", ".join(pricing.get("data_sources", []))}')
                
            else:
                # Full update
                result = pricing_manager.full_pricing_update(include_history=include_history)
                
                if result['success']:
                    stats = result['update_stats']
                    summary = result['pricing_summary']
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Pricing update completed successfully!')
                    )
                    self.stdout.write(f'📊 Cards processed: {result["cards_processed"]}')
                    self.stdout.write(f'💾 Database updates: {stats["updated"]}')
                    self.stdout.write(f'⚠️ Errors: {stats["errors"]}')
                    self.stdout.write(f'⏭️ Skipped: {stats["skipped"]}')
                    
                    if summary:
                        self.stdout.write('\n📈 Pricing Summary:')
                        self.stdout.write(f'Total cards with pricing: {summary["total_cards_with_pricing"]:,}')
                        self.stdout.write(f'Average price (USD): ${summary["average_price_usd"]:.2f}')
                        self.stdout.write(f'Price range: ${summary["lowest_price_usd"]:.2f} - ${summary["highest_price_usd"]:.2f}')
                        self.stdout.write(f'MTGjson data quality: {summary["data_quality"]:.1f}%')
                        
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Pricing update failed: {result["error"]}')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during pricing update: {e}')
            )
            logger.exception("Pricing update command failed")
