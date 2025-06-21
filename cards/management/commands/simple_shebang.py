"""
SIMPLE "Whole Shebang" command - queue everything and process it.
No complex logic, just get it done.
"""

from django.core.management.base import BaseCommand
from cards.job_queue import job_queue
from cards.analysis_manager import analysis_manager
import time

class Command(BaseCommand):
    """
    Simple whole shebang - queue and process ALL cards.
    """
    help = 'Simple whole shebang - queue and process all unanalyzed cards'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-cards',
            type=int,
            default=10,
            help='Maximum cards to process (default: 10)'
        )
        
        parser.add_argument(
            '--queue-only',
            action='store_true',
            help='Only queue cards, don\'t process them'
        )
    
    def handle(self, *args, **options):
        max_cards = options['max_cards']
        queue_only = options['queue_only']
        
        self.stdout.write(
            self.style.SUCCESS(f"🎯 SIMPLE SHEBANG - Processing {max_cards} cards")
        )
        
        # Step 1: Queue cards using the simple method
        jobs_queued = job_queue.queue_all_unanalyzed_simple(max_cards=max_cards)
        
        if jobs_queued == 0:
            self.stdout.write("ℹ️ No new jobs to queue")
            
        if queue_only:
            self.stdout.write(f"✅ Queued {jobs_queued} jobs. Done.")
            return
        
        # Step 2: Process jobs one by one
        self.stdout.write(f"🔄 Processing {jobs_queued} queued jobs...")
        
        jobs_processed = 0
        jobs_completed = 0
        jobs_failed = 0
        
        worker_id = "simple-shebang-worker"
        
        while True:
            # Get next job
            job = job_queue.get_next_job(worker_id)
            
            if not job:
                break  # No more jobs
            
            jobs_processed += 1
            card_uuid = job['card_uuid']
            job_id = job['job_id']
            
            self.stdout.write(f"🔄 [{jobs_processed}] Processing card {card_uuid[:8]}...")
            
            try:
                # Run the analysis
                success = analysis_manager.analyze_card_serial(card_uuid)
                
                if success:
                    job_queue.complete_job(job_id, success=True)
                    jobs_completed += 1
                    self.stdout.write(f"   ✅ Completed card {card_uuid[:8]}")
                else:
                    job_queue.complete_job(job_id, success=False, error_message="Analysis returned False")
                    jobs_failed += 1
                    self.stdout.write(f"   ❌ Failed card {card_uuid[:8]}")
                    
            except Exception as e:
                job_queue.complete_job(job_id, success=False, error_message=str(e))
                jobs_failed += 1
                self.stdout.write(f"   ❌ Error on card {card_uuid[:8]}: {e}")
            
            # Brief pause between cards
            time.sleep(1)
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"🎉 COMPLETE! Processed {jobs_processed} jobs: "
                f"✅{jobs_completed} ❌{jobs_failed}"
            )
        )
