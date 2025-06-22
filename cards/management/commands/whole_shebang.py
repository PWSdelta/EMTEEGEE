"""
Management command for the "whole shebang" - queue and process ALL unanalyzed cards.
Simple, effective, gets the job done.
"""

import time
import signal
import sys
from django.core.management.base import BaseCommand
from cards.job_queue import job_queue
from cards.models import get_cards_collection

class Command(BaseCommand):
    """
    The "whole shebang" - queue every unanalyzed card and process them sequentially.
    
    Usage:
        python manage.py whole_shebang [--dry-run] [--max-cards 1000]
    """
    help = 'Queue and process ALL unanalyzed cards - the whole shebang!'
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be queued without actually doing it'
        )
        
        parser.add_argument(
            '--max-cards',
            type=int,
            default=0,
            help='Maximum cards to queue (0 = all cards)'
        )
        
        parser.add_argument(
            '--skip-queue',
            action='store_true',
            help='Skip queueing step, just process existing queue'
        )
    
    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.max_cards = options['max_cards']
        self.skip_queue = options['skip_queue']
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.stdout.write(
            self.style.SUCCESS("🚀 THE WHOLE SHEBANG - EMTEEGEE CARD ANALYSIS")
        )
        self.stdout.write("=" * 60)
        
        if not self.skip_queue:
            # Step 1: Queue all unanalyzed cards
            self._queue_all_cards()
        
        if not self.dry_run:
            # Step 2: Process the entire queue
            self._process_entire_queue()
        
        self.stdout.write(
            self.style.SUCCESS("🎉 THE WHOLE SHEBANG IS COMPLETE!")
        )
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.stdout.write(
            self.style.WARNING(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        )
        self.running = False
    
    def _queue_all_cards(self):
        """Queue every single unanalyzed card."""
        self.stdout.write("📋 Step 1: Queueing ALL unanalyzed cards...")
        
        try:
            cards_collection = get_cards_collection()
            
            # Find ALL unanalyzed cards (simple query)
            unanalyzed_query = {
                "$or": [
                    {"analysis.fully_analyzed": {"$ne": True}},
                    {"analysis": {"$exists": False}},
                    {"analysis.component_count": {"$lt": 20}}
                ]
            }
            
            # Count total unanalyzed cards
            total_unanalyzed = cards_collection.count_documents(unanalyzed_query)
            self.stdout.write(f"   Found {total_unanalyzed:,} unanalyzed cards")
            
            if self.max_cards > 0 and self.max_cards < total_unanalyzed:
                limit = self.max_cards
                self.stdout.write(f"   Limiting to {limit:,} cards as requested")
            else:
                limit = total_unanalyzed
            
            if self.dry_run:
                self.stdout.write(f"   [DRY RUN] Would queue {limit:,} cards")
                return
            
            # Get existing jobs to avoid duplicates
            existing_job_cards = set()
            for job in job_queue.jobs_collection.find(
                {"status": {"$in": ["pending", "processing"]}}, 
                {"card_uuid": 1}
            ):
                existing_job_cards.add(job['card_uuid'])
            
            self.stdout.write(f"   Found {len(existing_job_cards)} existing jobs, skipping those")
            
            # Queue cards in batches for better performance
            batch_size = 1000
            jobs_queued = 0
            cards_processed = 0
            
            cursor = cards_collection.find(unanalyzed_query).limit(limit)
            
            for card in cursor:
                if not self.running:
                    break
                    
                cards_processed += 1
                
                # Skip if already has a job
                if card['uuid'] in existing_job_cards:
                    continue
                
                # Double-check analysis status
                analysis = card.get('analysis', {})
                if analysis.get('fully_analyzed') and analysis.get('component_count', 0) >= 20:
                    continue
                  # Queue the card with smart prioritization
                job_id = job_queue.enqueue_card_analysis_smart(card['uuid'])
                if job_id:
                    jobs_queued += 1
                  # Progress update every batch
                if cards_processed % batch_size == 0:
                    self.stdout.write(f"   📊 Processed {cards_processed:,}/{limit:,} cards, queued {jobs_queued:,} jobs")
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Queued {jobs_queued:,} cards for analysis!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error queueing cards: {e}")
            )
    
    def _process_entire_queue(self):
        """Process the job queue sequentially, respecting max_cards limit."""
        self.stdout.write("\n🔄 Step 2: Processing the queue...")
        
        # Get initial queue stats
        initial_stats = job_queue.get_queue_stats()
        total_pending = initial_stats['pending']
        
        if total_pending == 0:
            self.stdout.write("   ℹ️ No jobs in queue to process")
            return
        
        # Respect max_cards limit for processing too
        jobs_to_process = total_pending
        if self.max_cards > 0:
            jobs_to_process = min(total_pending, self.max_cards)
            self.stdout.write(f"   📊 Processing {jobs_to_process:,} jobs (limited from {total_pending:,} total)")
        else:
            self.stdout.write(f"   📊 Processing {total_pending:,} pending jobs...")
            
        self.stdout.write("   ⚡ Running in sequential mode for maximum reliability")
          # Import the worker command and run it properly
        from cards.management.commands.queue_worker import Command as WorkerCommand
        from io import StringIO
        
        jobs_processed = 0
        jobs_completed = 0
        jobs_failed = 0
        start_time = time.time()
        
        worker_id = "whole-shebang-worker"
        
        while self.running:
            # Get next job directly from the job queue
            job = job_queue.get_next_job(worker_id)
            
            if not job:
                # Check if there are still pending jobs (might be processing by other workers)
                current_stats = job_queue.get_queue_stats()
                if current_stats['pending'] == 0:
                    # Truly no more jobs
                    break
                else:
                    # Wait a bit and try again
                    time.sleep(1)
                    continue
            
            jobs_processed += 1
            
            # Check if we've hit our processing limit
            if self.max_cards > 0 and jobs_processed > jobs_to_process:
                self.stdout.write(f"   ✅ Reached processing limit of {jobs_to_process:,} jobs")
                break
            
            # Process the job using the analysis manager directly
            try:
                card_uuid = job['card_uuid']
                job_type = job['job_type']
                job_id = job['job_id']
                
                self.stdout.write(f"   🔄 Processing {job_type} for card {card_uuid[:8]}...")
                  # Import analysis manager here to avoid circular imports
                from cards.analysis_manager import analysis_manager
                
                success = False
                if job_type == 'full_analysis':
                    # Run full analysis using the correct method
                    result = analysis_manager.generate_all_components_serial_by_speed(card_uuid)
                    success = result and any(result.values())  # Success if any component was generated
                elif job_type.startswith('single_component_'):
                    # Run single component analysis
                    component_type = job_type.replace('single_component_', '')
                    success = analysis_manager.generate_component(card_uuid, component_type)
                else:
                    self.stdout.write(f"   ❌ Unknown job type: {job_type}")
                    success = False
                
                # Complete the job
                if success:
                    job_queue.complete_job(job_id, success=True, metadata={'processed_by': worker_id})
                    jobs_completed += 1
                    self.stdout.write(f"   ✅ Completed {job_type} for {card_uuid[:8]}")
                else:
                    job_queue.complete_job(job_id, success=False, error_message="Analysis failed")
                    jobs_failed += 1
                    self.stdout.write(f"   ❌ Failed {job_type} for {card_uuid[:8]}")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Error processing job: {e}")
                job_queue.complete_job(job.get('job_id'), success=False, error_message=str(e))
                jobs_failed += 1
            
            # Progress update every 10 jobs
            if jobs_processed % 10 == 0:
                elapsed = time.time() - start_time
                rate = jobs_processed / elapsed if elapsed > 0 else 0
                remaining = total_pending - jobs_processed
                eta = remaining / rate if rate > 0 else 0
                
                self.stdout.write(
                    f"   📊 Progress: {jobs_processed:,}/{total_pending:,} "
                    f"(✅{jobs_completed} ❌{jobs_failed}) "
                    f"Rate: {rate:.1f}/min ETA: {eta/60:.1f}min"
                )
        
        # Final summary
        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎯 Processing complete! "
                f"Processed {jobs_processed:,} jobs in {elapsed/60:.1f} minutes"
            )
        )
        self.stdout.write(f"   ✅ Completed: {jobs_completed:,}")
        self.stdout.write(f"   ❌ Failed: {jobs_failed:,}")
        
        # Final queue stats
        final_stats = job_queue.get_queue_stats()
        self.stdout.write(f"   📊 Final queue: {final_stats}")
