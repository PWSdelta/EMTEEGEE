"""
Minimal job queue for basic functionality.
"""


class JobQueue:
    """Basic job queue implementation."""
    
    def __init__(self):
        self.jobs = []
    
    def get_status(self):
        """Get job queue status."""
        return {
            'pending_jobs': 0,
            'processing_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0
        }
    
    def add_job(self, job_data):
        """Add a job to the queue."""
        self.jobs.append(job_data)
        return len(self.jobs) - 1
    
    def get_jobs(self):
        """Get all jobs."""
        return self.jobs


# Create a global instance
job_queue = JobQueue()
