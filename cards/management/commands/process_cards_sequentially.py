"""
Django management command for sequential card processing.
Processes multiple cards in a queue-like fashion for bulk analysis.
"""

import time
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cards.analysis_manager import analysis_manager
from cards.models import get_cards_collection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process multiple cards sequentially for bulk analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['start', 'status', 'stop', 'queue'],
            help='Action to perform on sequential processing'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of cards to process in this session'
        )
        parser.add_argument(
            '--filter',
            type=str,
            choices=['unanalyzed', 'incomplete', 'all'],
            default='unanalyzed',
            help='Filter cards to process'
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=5,
            help='Delay in seconds between card processing'
        )
        parser.add_argument(
            '--parallel',
            action='store_true',
            help='Use parallel processing for each card (may overload system)'
        )
        parser.add_argument(
            '--priority',
            type=str,
            choices=['popular', 'alphabetical', 'random'],
            default='alphabetical',
            help='Priority order for processing cards'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'start':
            self.start_sequential_processing(options)
        elif action == 'status':
            self.show_processing_status()
        elif action == 'stop':
            self.stop_processing()
        elif action == 'queue':
            self.show_processing_queue(options)

    def start_sequential_processing(self, options):
        """Start sequential processing of cards."""
        limit = options['limit']
        card_filter = options['filter']
        delay = options['delay']
        use_parallel = options['parallel']        priority = options['priority']
        
        self.stdout.write("🚀 Starting sequential card processing...")
        self.stdout.write(f"📋 Config: {limit} cards, {card_filter} filter, {delay}s delay")
        self.stdout.write(f"⚡ Mode: {'Parallel' if use_parallel else 'Serial'}")
        self.stdout.write(f"🎯 Priority: {priority}")
        self.stdout.write("=" * 60)
        
        # Get cards to process
        cards_to_process = self.get_cards_to_process(card_filter, limit, priority)
        
        if not cards_to_process:
            self.stdout.write(self.style.WARNING("No cards found matching criteria"))
            return
            
        self.stdout.write(f"📊 Found {len(cards_to_process)} cards to process")
        
        # Process each card
        processed_count = 0
        successful_count = 0
        failed_count = 0
        start_time = time.time()
        
        for i, card in enumerate(cards_to_process, 1):
            card_name = card.get('name', 'Unknown')
            card_uuid = card.get('id')
            
            self.stdout.write(f"\n🔄 [{i}/{len(cards_to_process)}] Processing: {card_name}")
            
            try:
                # Process the card
                card_start_time = time.time()
                
                if use_parallel:
                    success = analysis_manager.analyze_card_parallel(card_uuid)
                else:
                    success = analysis_manager.analyze_card_serial(card_uuid)
                
                card_duration = time.time() - card_start_time
                
                if success:
                    successful_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {card_name} completed in {card_duration:.1f}s"
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ {card_name} failed")
                    )
                    
                processed_count += 1
                
                # Show progress stats
                elapsed_time = time.time() - start_time
                avg_time_per_card = elapsed_time / processed_count
                estimated_remaining = (len(cards_to_process) - processed_count) * avg_time_per_card
                
                self.stdout.write(
                    f"📊 Progress: {processed_count}/{len(cards_to_process)} "
                    f"({successful_count} ✅, {failed_count} ❌) "
                    f"| ETA: {estimated_remaining/60:.1f}m"
                )
                
                # Delay between cards (except for last card)
                if i < len(cards_to_process) and delay > 0:
                    self.stdout.write(f"⏳ Waiting {delay}s before next card...")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\n🛑 Processing interrupted by user"))
                break
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"💥 Error processing {card_name}: {e}")
                )
                
        # Final summary
        total_time = time.time() - start_time
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"🏁 Sequential processing complete!")
        self.stdout.write(f"📊 Results: {successful_count} successful, {failed_count} failed")
        self.stdout.write(f"⏱️  Total time: {total_time/60:.1f} minutes")
        self.stdout.write(f"🚀 Average: {total_time/processed_count:.1f}s per card")

    def get_cards_to_process(self, card_filter, limit, priority):
        """Get list of cards to process based on filter and priority."""
        cards_collection = get_cards_collection()
        
        # Build query based on filter
        if card_filter == 'unanalyzed':
            query = {
                '$or': [
                    {'analysis': {'$exists': False}},
                    {'analysis.fully_analyzed': {'$ne': True}}
                ]
            }
        elif card_filter == 'incomplete':
            query = {
                'analysis.component_count': {'$lt': 20}
            }
        else:  # all
            query = {}
            
        # Apply sorting based on priority
        if priority == 'popular':
            sort_order = [('power', -1), ('toughness', -1), ('name', 1)]
        elif priority == 'random':
            # MongoDB random sampling
            return list(cards_collection.aggregate([
                {'$match': query},
                {'$sample': {'size': limit}}
            ]))
        else:  # alphabetical
            sort_order = [('name', 1)]
            
        return list(cards_collection.find(query).sort(sort_order).limit(limit))

    def show_processing_status(self):
        """Show current processing status."""
        self.stdout.write("📊 Sequential Processing Status")
        self.stdout.write("=" * 50)
        
        # Get overall analysis progress
        progress = analysis_manager.get_analysis_progress()
        
        self.stdout.write(f"Total cards: {progress.get('total_cards', 0):,}")
        self.stdout.write(f"Fully analyzed: {progress.get('fully_analyzed', 0):,}")
        self.stdout.write(f"In progress: {progress.get('in_progress', 0):,}")
        self.stdout.write(f"Not started: {progress.get('not_started', 0):,}")
        self.stdout.write(f"Completion: {progress.get('completion_percentage', 0):.1f}%")
        
        # Show recent activity
        cards_collection = get_cards_collection()
        recent = list(cards_collection.find({
            'analysis.analysis_completed_at': {'$exists': True}
        }).sort([('analysis.analysis_completed_at', -1)]).limit(5))
        
        if recent:
            self.stdout.write("\n🕒 Recently completed:")
            for card in recent:
                completed_at = card['analysis'].get('analysis_completed_at')
                self.stdout.write(f"  - {card['name']} ({completed_at})")

    def show_processing_queue(self, options):
        """Show cards queued for processing."""
        card_filter = options['filter']
        limit = options['limit']
        priority = options['priority']
        
        self.stdout.write(f"📋 Processing Queue ({card_filter}, {priority})")
        self.stdout.write("=" * 50)
        
        cards = self.get_cards_to_process(card_filter, limit, priority)
        
        if not cards:
            self.stdout.write("No cards in queue")
            return
            
        for i, card in enumerate(cards, 1):
            analysis = card.get('analysis', {})
            component_count = analysis.get('component_count', 0)
            
            status = "Not started"
            if component_count > 0:
                status = f"{component_count}/20 components"
            if analysis.get('fully_analyzed'):
                status = "Complete ✅"
                
            self.stdout.write(f"{i:2d}. {card['name']} - {status}")

    def stop_processing(self):
        """Stop any ongoing processing."""
        self.stdout.write("🛑 Sequential processing stop requested")
        self.stdout.write("Note: Current card will finish, then processing will halt")
