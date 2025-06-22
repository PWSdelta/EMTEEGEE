#!/usr/bin/env python3
"""Simple script to populate job queue with EDHREC priorities."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def populate_queue():
    """Populate the job queue with EDHREC rank-based priorities."""
    try:
        from cards.job_queue import job_queue
        
        print('🎯 Populating job queue with EDHREC rank-based priorities...')
        jobs_added = job_queue.queue_all_unanalyzed_simple()
        print(f'✅ Added {jobs_added} jobs to the queue')
          # Show queue status
        stats = job_queue.get_queue_stats()
        print(f"📊 Queue Stats: {stats}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_queue()
