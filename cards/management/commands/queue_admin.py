"""
Management command for queue operations and monitoring.
"""

import time
from django.core.management.base import BaseCommand
from cards.job_queue import job_queue
from cards.models import get_cards_collection
from cards.models import get_cards_collection

class Command(BaseCommand):
    """
    Management command for job queue operations.
    
    Usage:
        python manage.py queue_admin status
        python manage.py queue_admin cleanup --days 7
        python manage.py queue_admin reset-stuck --hours 2
        python manage.py queue_admin bulk-queue --limit 50
        python manage.py queue_admin retry-failed
        python manage.py queue_admin monitor --refresh 5
    """
    help = 'Job queue administration and monitoring'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['status', 'cleanup', 'reset-stuck', 'bulk-queue', 'retry-failed', 'monitor'],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Days old for cleanup operations'
        )
        
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Hours old for stuck job reset'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Limit for bulk operations'
        )
        
        parser.add_argument(
            '--refresh',
            type=int,
            default=5,
            help='Refresh interval for monitoring (seconds)'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'status':
            self._show_status()
        elif action == 'cleanup':
            self._cleanup_jobs(options['days'])
        elif action == 'reset-stuck':
            self._reset_stuck_jobs(options['hours'])
        elif action == 'bulk-queue':
            self._bulk_queue_cards(options['limit'])
        elif action == 'retry-failed':
            self._retry_failed_jobs()
        elif action == 'monitor':
            self._monitor_queue(options['refresh'])
    
    def _show_status(self):
        """Show current queue status."""
        self.stdout.write(self.style.SUCCESS("📊 Job Queue Status"))
        self.stdout.write("=" * 50)
        
        # Get queue stats
        stats = job_queue.get_queue_stats()
        total_jobs = sum(stats.values())
        
        self.stdout.write(f"📋 Total Jobs: {total_jobs}")
        self.stdout.write(f"⏳ Pending: {stats['pending']}")
        self.stdout.write(f"🔄 Processing: {stats['processing']}")
        self.stdout.write(f"✅ Completed: {stats['completed']}")
        self.stdout.write(f"❌ Failed: {stats['failed']}")
        
        # Show recent jobs
        recent_jobs = job_queue.get_recent_jobs(limit=10)
        if recent_jobs:
            self.stdout.write("\n🕒 Recent Jobs:")
            for job in recent_jobs[:5]:
                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(job['status'], '❓')
                
                self.stdout.write(
                    f"  {status_emoji} {job['job_id'][:8]}... | "
                    f"{job['job_type']} | "
                    f"Card: {job['card_uuid'][:8]}... | "
                    f"Attempts: {job.get('attempts', 0)}"
                )
          # Analysis progress
        try:
            from cards.models import get_cards_collection
            cards_collection = get_cards_collection()
            total_cards = cards_collection.count_documents({})
            analyzed_cards = cards_collection.count_documents({'analysis.fully_analyzed': True})
            progress = (analyzed_cards / total_cards * 100) if total_cards > 0 else 0
            
            self.stdout.write(f"\n🎯 Analysis Progress: {analyzed_cards:,}/{total_cards:,} ({progress:.1f}%)")
            
        except Exception as e:
            self.stdout.write(f"\n⚠️ Could not get analysis progress: {e}")
    
    def _cleanup_jobs(self, days_old):
        """Clean up old completed/failed jobs."""
        self.stdout.write(f"🧹 Cleaning up jobs older than {days_old} days...")
        
        cleaned_count = job_queue.cleanup_old_jobs(days_old=days_old)
        
        if cleaned_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Cleaned up {cleaned_count} old jobs")
            )
        else:
            self.stdout.write("ℹ️ No old jobs found to clean up")
    
    def _reset_stuck_jobs(self, hours_old):
        """Reset stuck jobs."""
        self.stdout.write(f"🔧 Resetting jobs stuck for more than {hours_old} hours...")
        
        reset_count = job_queue.reset_stuck_jobs(hours_old=hours_old)
        
        if reset_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Reset {reset_count} stuck jobs")
            )
        else:
            self.stdout.write("ℹ️ No stuck jobs found")
    
    def _bulk_queue_cards(self, limit):
        """Bulk queue unanalyzed cards."""
        self.stdout.write(f"📋 Queueing up to {limit} unanalyzed cards...")
        
        jobs_enqueued = job_queue.bulk_enqueue_unanalyzed_cards(limit=limit)
        
        if jobs_enqueued > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Queued {jobs_enqueued} cards for analysis")
            )
        else:
            self.stdout.write("ℹ️ No unanalyzed cards found to queue")
    
    def _retry_failed_jobs(self):
        """Retry all failed jobs that haven't exceeded max attempts."""
        self.stdout.write("🔄 Retrying failed jobs...")
        
        # Find failed jobs that can be retried
        failed_jobs = list(job_queue.jobs_collection.find({
            'status': 'failed',
            'attempts': {'$lt': 3}  # Haven't exceeded max attempts
        }))
        
        retry_count = 0
        for job in failed_jobs:
            if job_queue.requeue_failed_job(job['job_id']):
                retry_count += 1
        
        if retry_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Requeued {retry_count} failed jobs")
            )
        else:
            self.stdout.write("ℹ️ No failed jobs available for retry")
    
    def _monitor_queue(self, refresh_interval):
        """Real-time queue monitoring."""
        self.stdout.write(
            self.style.SUCCESS(f"🖥️ Monitoring queue (refreshing every {refresh_interval}s)")
        )
        self.stdout.write("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                # Clear screen (works on most terminals)
                self.stdout.write("\033[2J\033[H")
                
                # Show timestamp
                from datetime import datetime
                self.stdout.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.stdout.write("=" * 60)
                
                # Show current stats
                stats = job_queue.get_queue_stats()
                self.stdout.write(
                    f"📊 Queue: "
                    f"Pending: {stats['pending']} | "
                    f"Processing: {stats['processing']} | "
                    f"Completed: {stats['completed']} | "
                    f"Failed: {stats['failed']}"
                )
                
                # Show recent activity
                recent_jobs = job_queue.get_recent_jobs(limit=8)
                if recent_jobs:
                    self.stdout.write("\n🕒 Recent Activity:")
                    for job in recent_jobs:
                        status_emoji = {
                            'pending': '⏳',
                            'processing': '🔄',
                            'completed': '✅',
                            'failed': '❌'
                        }.get(job['status'], '❓')
                        
                        # Format timestamp
                        created = job.get('created_at')
                        time_str = created.strftime('%H:%M:%S') if created else 'Unknown'
                        
                        self.stdout.write(
                            f"  {status_emoji} [{time_str}] {job['job_type']} | "
                            f"Card: {job['card_uuid'][:8]}... | "
                            f"Attempts: {job.get('attempts', 0)}"
                        )
                
                # Wait before next refresh
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            self.stdout.write("\n\n🛑 Monitoring stopped")
