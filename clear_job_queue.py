#!/usr/bin/env python
"""
Clear the entire job queue to start fresh after deleting cards.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.job_queue import JobQueue

def clear_job_queue():
    """Clear all jobs from the queue."""
    print("🗑️ Clearing Job Queue")
    print("=" * 50)
    
    try:
        job_queue = JobQueue()
        
        # Get current queue stats first
        stats = job_queue.get_queue_stats()
        print(f"📊 Current Queue Status:")
        print(f"  - Pending: {stats.get('pending', 0)}")
        print(f"  - Processing: {stats.get('processing', 0)}")
        print(f"  - Completed: {stats.get('completed', 0)}")
        print(f"  - Failed: {stats.get('failed', 0)}")
        print(f"  - Total: {sum(stats.values())}")
        
        if sum(stats.values()) == 0:
            print("✅ Queue is already empty!")
            return
        
        # Clear all jobs
        print("\n🗑️ Clearing all jobs...")
        result = job_queue.jobs_collection.delete_many({})
        deleted_count = result.deleted_count
        
        print(f"✅ Deleted {deleted_count} jobs from queue")
        
        # Verify it's empty
        final_stats = job_queue.get_queue_stats()
        print(f"\n📊 Final Queue Status:")
        print(f"  - Pending: {final_stats.get('pending', 0)}")
        print(f"  - Processing: {final_stats.get('processing', 0)}")
        print(f"  - Completed: {final_stats.get('completed', 0)}")
        print(f"  - Failed: {final_stats.get('failed', 0)}")
        print(f"  - Total: {sum(final_stats.values())}")
        
        if sum(final_stats.values()) == 0:
            print("🎉 Job queue successfully cleared!")
            print("Ready for fresh smart prioritization!")
        else:
            print("⚠️ Some jobs may still remain")
        
    except Exception as e:
        print(f"❌ Error clearing queue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_job_queue()
