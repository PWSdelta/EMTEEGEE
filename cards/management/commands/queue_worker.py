"""
Management command to run the MongoDB job queue worker for card analysis.
This is a robust, production-ready worker with retry logic and error handling.
"""

import time
import signal
import sys
import uuid
import logging
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.utils import timezone as django_timezone

from cards.job_queue import job_queue
from cards.analysis_manager import analysis_manager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Worker command for processing card analysis jobs from MongoDB queue.
    
    Usage:
        python manage.py queue_worker [--worker-id custom-id] [--max-jobs 100] [--idle-timeout 300]
    """
    help = 'Run job queue worker for card analysis'
    
    def __init__(self):
        super().__init__()
        self.worker_id = str(uuid.uuid4())
        self.running = True
        self.jobs_processed = 0
        self.start_time = None
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--worker-id',
            type=str,
            default=None,
            help='Custom worker ID (default: random UUID)'
        )
        
        parser.add_argument(
            '--max-jobs',
            type=int,
            default=0,
            help='Maximum jobs to process before stopping (0 = unlimited)'
        )
        
        parser.add_argument(
            '--idle-timeout',
            type=int,
            default=300,
            help='Seconds to wait when queue is empty before checking again'
        )
        
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Run cleanup operations before starting worker'
        )
        
        parser.add_argument(
            '--stats-interval',
            type=int,
            default=60,
            help='Seconds between status reports'
        )
    
    def handle(self, *args, **options):
        # Set up worker
        if options['worker_id']:
            self.worker_id = options['worker_id']
        
        self.max_jobs = options['max_jobs']
        self.idle_timeout = options['idle_timeout']
        self.cleanup = options['cleanup']
        self.stats_interval = options['stats_interval']
        self.start_time = datetime.now(timezone.utc)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
          # Log startup
        self.stdout.write(
            self.style.SUCCESS("🚀 Starting EMTEEGEE queue worker")
        )
        self.stdout.write(f"   Worker ID: {self.worker_id}")
        self.stdout.write(f"   Max jobs: {'unlimited' if self.max_jobs == 0 else self.max_jobs}")
        self.stdout.write(f"   Idle timeout: {self.idle_timeout}s")
        
        # Run cleanup if requested
        if self.cleanup:
            self._run_cleanup()
        
        # Start processing jobs
        self._run_worker()
        
        # Shutdown summary
        runtime = datetime.now(timezone.utc) - self.start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"🏁 Worker {self.worker_id[:8]}... processed {self.jobs_processed} jobs in {runtime}"
            )
        )
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.stdout.write(
            self.style.WARNING(f"🛑 Received signal {signum}, shutting down gracefully...")
        )
        self.running = False
    
    def _run_cleanup(self):
        """Run maintenance operations on the job queue."""
        self.stdout.write("🧹 Running queue cleanup operations...")
        
        # Reset stuck jobs
        stuck_count = job_queue.reset_stuck_jobs(hours_old=2)
        if stuck_count > 0:
            self.stdout.write(f"   Reset {stuck_count} stuck jobs")
        
        # Clean up old jobs
        cleaned_count = job_queue.cleanup_old_jobs(days_old=7)
        if cleaned_count > 0:
            self.stdout.write(f"   Cleaned up {cleaned_count} old jobs")
        
        # Show current stats
        stats = job_queue.get_queue_stats()
        self.stdout.write(f"   Queue stats: {stats}")
    
    def _run_worker(self):
        """Main worker loop."""
        last_stats_time = time.time()
        consecutive_empty_checks = 0
        
        while self.running:
            try:
                # Get next job
                job = job_queue.get_next_job(self.worker_id)
                
                if job:
                    # Reset empty check counter
                    consecutive_empty_checks = 0
                      # Process the job
                    self._process_job(job)
                    self.jobs_processed += 1
                    
                    # Check if we've hit max jobs limit
                    if self.max_jobs > 0 and self.jobs_processed >= self.max_jobs:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Reached max jobs limit ({self.max_jobs}), stopping")
                        )
                        break
                
                else:
                    # No jobs available
                    consecutive_empty_checks += 1
                    
                    if consecutive_empty_checks == 1:
                        self.stdout.write("⏳ Queue empty, waiting for jobs...")
                    
                    # Progressive backoff when queue is empty
                    wait_time = min(self.idle_timeout, consecutive_empty_checks * 5)
                    time.sleep(wait_time)
                
                # Periodic stats reporting
                if time.time() - last_stats_time >= self.stats_interval:
                    self._report_stats()
                    last_stats_time = time.time()
                
            except KeyboardInterrupt:
                self.stdout.write("\n🛑 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                self.stdout.write(
                    self.style.ERROR(f"❌ Worker error: {e}")
                )
                time.sleep(5)  # Brief pause before continuing
    
    def _process_job(self, job):
        """
        Process a single job with robust error handling and retries.
        
        Args:
            job: Job document from MongoDB
            
        Returns:
            bool: True if job completed successfully
        """
        job_id = job['job_id']
        card_uuid = job['card_uuid']
        job_type = job['job_type']
        attempt = job.get('attempts', 1)
        
        self.stdout.write(
            f"🔄 Processing {job_type} for card {card_uuid[:8]}... (attempt {attempt}/{job.get('max_attempts', 3)})"
        )
        
        try:
            # Determine the type of analysis to perform
            if job_type == 'full_analysis':
                success = self._run_full_analysis(card_uuid)
            elif job_type.startswith('single_component_'):
                component_type = job_type.replace('single_component_', '')
                success = self._run_single_component_analysis(card_uuid, component_type)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Complete the job
            if success:
                job_queue.complete_job(
                    job_id, 
                    success=True,
                    metadata={'processed_by': self.worker_id, 'attempt': attempt}
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Completed {job_type} for {card_uuid[:8]}...")
                )
                return True
            else:
                # Job failed but didn't raise exception
                error_msg = f"Analysis returned False for {job_type}"
                self._handle_job_failure(job_id, error_msg, attempt, job.get('max_attempts', 3))
                return False
                
        except Exception as e:
            error_msg = f"Exception in {job_type}: {str(e)}"
            logger.error(f"Job {job_id[:8]}... failed: {error_msg}")
            self._handle_job_failure(job_id, error_msg, attempt, job.get('max_attempts', 3))
            return False
    
    def _handle_job_failure(self, job_id, error_msg, attempt, max_attempts):
        """Handle job failure with appropriate retry logic."""
        if attempt >= max_attempts:
            # Permanent failure
            job_queue.complete_job(job_id, success=False, error_message=error_msg)
            self.stdout.write(
                self.style.ERROR(f"❌ Job {job_id[:8]}... permanently failed: {error_msg}")
            )
        else:
            # Temporary failure - will be retried
            job_queue.complete_job(job_id, success=False, error_message=f"Attempt {attempt} failed: {error_msg}")
            self.stdout.write(
                self.style.WARNING(f"⚠️ Job {job_id[:8]}... failed (attempt {attempt}/{max_attempts}): {error_msg}")
            )
    
    def _run_full_analysis(self, card_uuid):
        """Run full analysis for a card."""
        try:
            return analysis_manager.analyze_card_serial(card_uuid)
        except Exception as e:
            logger.error(f"Full analysis failed for {card_uuid}: {e}")
            return False
    
    def _run_single_component_analysis(self, card_uuid, component_type):
        """Run single component analysis for a card."""
        try:
            return analysis_manager.generate_component(card_uuid, component_type)
        except Exception as e:
            logger.error(f"Component analysis ({component_type}) failed for {card_uuid}: {e}")
            return False
    
    def _report_stats(self):
        """Report current worker statistics."""
        runtime = datetime.now(timezone.utc) - self.start_time
        stats = job_queue.get_queue_stats()
        
        self.stdout.write(
            f"📊 Worker {self.worker_id[:8]}... | "
            f"Runtime: {runtime} | "
            f"Processed: {self.jobs_processed} | "
            f"Queue: P:{stats['pending']} R:{stats['processing']} "
            f"C:{stats['completed']} F:{stats['failed']}"
        )
