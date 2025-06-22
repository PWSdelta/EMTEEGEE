"""
MongoDB-based job queue system for EMTEEGEE card analysis.
Simple, reliable, and uses existing MongoDB infrastructure.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.collection import Collection
import uuid

logger = logging.getLogger(__name__)

class JobQueue:
    """MongoDB-based job queue for card analysis tasks."""
    
    def __init__(self, db_name: str = "emteegee", collection_name: str = "analysis_jobs"):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.jobs_collection: Collection = self.db[collection_name]
        
        # Create indexes for efficient querying
        self._create_indexes()
        
    def _create_indexes(self):
        """Create MongoDB indexes for efficient job processing."""
        try:
            # Index for finding pending jobs quickly
            self.jobs_collection.create_index([
                ("status", 1), 
                ("priority", -1), 
                ("created_at", 1)
            ])
            
            # Index for cleanup and monitoring
            self.jobs_collection.create_index([("created_at", 1)])
            
            # Unique index to prevent duplicate jobs
            self.jobs_collection.create_index([
                ("card_uuid", 1), 
                ("job_type", 1)
            ], unique=True, sparse=True)
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def enqueue_card_analysis(self, card_uuid: str, priority: int = 0, 
                            job_type: str = "full_analysis") -> Optional[str]:
        """
        Add a card analysis job to the queue.
        
        Args:
            card_uuid: UUID of the card to analyze
            priority: Job priority (higher = processed first)
            job_type: Type of analysis ('full_analysis', 'single_component', etc.)
            
        Returns:
            Job ID if successful, None if failed
        """
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "card_uuid": card_uuid,
            "job_type": job_type,
            "status": "pending",  # pending, processing, completed, failed
            "priority": priority,
            "created_at": datetime.now(timezone.utc),
            "started_at": None,
            "completed_at": None,
            "attempts": 0,
            "max_attempts": 3,
            "error_message": None,
            "worker_id": None,
            "metadata": {}
        }
        
        try:
            # Try to insert, handle duplicates gracefully
            self.jobs_collection.insert_one(job_data)
            logger.info(f"🎯 Queued {job_type} job for card {card_uuid[:8]}... (Job: {job_id[:8]}...)")
            return job_id
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.info(f"⚠️ Job already exists for card {card_uuid[:8]}...")
                return None
            else:
                logger.error(f"Error enqueuing job: {e}")
                return None
    
    def get_next_job(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next pending job and mark it as processing.
        Uses atomic findAndModify to prevent race conditions.
        
        Args:
            worker_id: Unique identifier for the worker
            
        Returns:
            Job document if found, None if no jobs available
        """
        try:            # Atomic operation: find pending job and mark as processing
            job = self.jobs_collection.find_one_and_update(
                {
                    "status": "pending",
                    "attempts": {"$lt": 3}  # Simple hardcoded limit for now
                },
                {
                    "$set": {
                        "status": "processing",
                        "started_at": datetime.now(timezone.utc),
                        "worker_id": worker_id
                    },
                    "$inc": {"attempts": 1}
                },
                sort=[("priority", -1), ("created_at", 1)],  # High priority first, then FIFO
                return_document=True
            )
            
            if job:
                logger.info(f"🚀 Worker {worker_id[:8]}... picked up job {job['job_id'][:8]}... for card {job['card_uuid'][:8]}...")
            
            return job
            
        except Exception as e:
            logger.error(f"Error getting next job: {e}")
            return None
    
    def complete_job(self, job_id: str, success: bool = True, 
                    error_message: str = None, metadata: Dict = None) -> bool:
        """
        Mark a job as completed or failed.
        
        Args:
            job_id: Job ID to update
            success: Whether the job succeeded
            error_message: Error message if failed
            metadata: Additional metadata to store
            
        Returns:
            True if updated successfully
        """
        update_data = {
            "completed_at": datetime.now(timezone.utc),
            "status": "completed" if success else "failed"
        }
        
        if error_message:
            update_data["error_message"] = error_message
            
        if metadata:
            update_data["metadata"] = metadata
        
        try:
            result = self.jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                status_emoji = "✅" if success else "❌"
                logger.info(f"{status_emoji} Job {job_id[:8]}... {'completed' if success else 'failed'}")
                return True
            else:
                logger.warning(f"Job {job_id[:8]}... not found for completion")
                return False
                
        except Exception as e:
            logger.error(f"Error completing job {job_id[:8]}...: {e}")
            return False
    
    def requeue_failed_job(self, job_id: str) -> bool:
        """Reset a failed job back to pending status for retry."""
        try:
            result = self.jobs_collection.update_one(
                {"job_id": job_id, "status": "failed"},
                {
                    "$set": {
                        "status": "pending",
                        "started_at": None,
                        "worker_id": None,
                        "error_message": None
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"🔄 Requeued failed job {job_id[:8]}...")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error requeuing job {job_id[:8]}...: {e}")
            return False
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get current queue statistics."""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            
            stats = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
            for result in self.jobs_collection.aggregate(pipeline):
                stats[result["_id"]] = result["count"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
    
    def cleanup_old_jobs(self, days_old: int = 7) -> int:
        """Remove completed jobs older than specified days."""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            result = self.jobs_collection.delete_many({
                "status": {"$in": ["completed", "failed"]},
                "completed_at": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 Cleaned up {result.deleted_count} old jobs")
            
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {e}")
            return 0
    
    def reset_stuck_jobs(self, hours_old: int = 2) -> int:
        """Reset jobs that have been processing for too long."""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(hours=hours_old)
            result = self.jobs_collection.update_many(
                {
                    "status": "processing",
                    "started_at": {"$lt": cutoff_date}
                },
                {
                    "$set": {
                        "status": "pending",
                        "started_at": None,
                        "worker_id": None
                    }
                }            )
            
            if result.modified_count > 0:
                logger.warning(f"🔧 Reset {result.modified_count} stuck jobs")
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error resetting stuck jobs: {e}")
            return 0
    
    def get_recent_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent jobs for monitoring dashboard."""
        try:
            return list(self.jobs_collection.find().sort("created_at", -1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting recent jobs: {e}")
            return []
    
    def bulk_enqueue_unanalyzed_cards(self, limit: int = 100) -> int:
        """
        Find unanalyzed cards and add them to the job queue.
        Skips cards that are already fully analyzed or have pending/processing jobs.
        
        Args:
            limit: Maximum number of cards to queue
            
        Returns:
            Number of jobs enqueued
        """
        try:
            # Get cards collection
            cards_collection = self.db['cards']
            
            # Get cards that already have pending or processing jobs to avoid duplicates
            existing_job_cards = set()
            for job in self.jobs_collection.find(
                {"status": {"$in": ["pending", "processing"]}}, 
                {"card_uuid": 1}
            ):
                existing_job_cards.add(job['card_uuid'])
              # Find unanalyzed cards that don't have existing jobs
            # Simplified query for debugging
            unanalyzed_query = {
                "$and": [
                    {
                        "$or": [
                            {"analysis.fully_analyzed": {"$ne": True}},
                            {"analysis": {"$exists": False}}
                        ]
                    },
                    {
                        "uuid": {"$nin": list(existing_job_cards)}
                    }                ]
            }
            
            logger.info(f"🔍 Searching for unanalyzed cards with query: {unanalyzed_query}")
            logger.info(f"🚫 Excluding {len(existing_job_cards)} cards with existing jobs")
            
            unanalyzed_cards = cards_collection.find(unanalyzed_query).limit(limit)
            
            jobs_enqueued = 0
            skipped_analyzed = 0
            cards_processed = 0
            
            for card in unanalyzed_cards:
                cards_processed += 1
                logger.debug(f"🔄 Processing card {cards_processed}: {card.get('name', 'Unknown')}")
                
                # Double-check the card isn't fully analyzed
                analysis = card.get('analysis', {})
                component_count = analysis.get('component_count', 0)
                fully_analyzed = analysis.get('fully_analyzed', False)
                
                logger.debug(f"   Analysis status: fully_analyzed={fully_analyzed}, component_count={component_count}")
                
                if fully_analyzed and component_count >= 20:
                    skipped_analyzed += 1
                    logger.debug(f"⏭️ Skipping already analyzed card {card['uuid'][:8]}...")
                    continue
                
                if self.enqueue_card_analysis_smart(card['uuid']):
                    jobs_enqueued += 1
            
            logger.info(f"📊 Processed {cards_processed} candidate cards")
            
            if skipped_analyzed > 0:
                logger.info(f"⏭️ Skipped {skipped_analyzed} already analyzed cards")
            
            logger.info(f"📋 Bulk enqueued {jobs_enqueued} card analysis jobs")
            return jobs_enqueued
            
        except Exception as e:
            logger.error(f"Error bulk enqueuing cards: {e}")
            return 0
        
    def get_failed_jobs_summary(self) -> Dict[str, Any]:
        """Get a summary of failed jobs for analysis."""
        try:
            pipeline = [
                {"$match": {"status": "failed"}},
                {"$group": {
                    "_id": {
                        "job_type": "$job_type",
                        "error_pattern": {"$substr": ["$error_message", 0, 50]}
                    },
                    "count": {"$sum": 1},
                    "sample_errors": {"$push": "$error_message"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            failure_patterns = list(self.jobs_collection.aggregate(pipeline))
            
            return {
                "failure_patterns": failure_patterns,
                "total_failed": self.jobs_collection.count_documents({"status": "failed"}),                "retryable_failed": self.jobs_collection.count_documents({
                    "status": "failed",
                    "attempts": {"$lt": 3}
                })
            }
            
        except Exception as e:
            logger.error(f"Error getting failed jobs summary: {e}")
            return {"failure_patterns": [], "total_failed": 0, "retryable_failed": 0}
    
    def update_job_priority(self, job_id: str, new_priority: int) -> bool:
        """Update the priority of a pending job."""
        try:
            result = self.jobs_collection.update_one(
                {"job_id": job_id, "status": "pending"},
                {"$set": {"priority": new_priority}}
            )
            
            if result.modified_count > 0:
                logger.info(f"🔄 Updated priority for job {job_id[:8]}... to {new_priority}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating job priority: {e}")
            return False
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        try:
            result = self.jobs_collection.update_one(
                {"job_id": job_id, "status": "pending"},
                {
                    "$set": {
                        "status": "cancelled",
                        "completed_at": datetime.now(timezone.utc),
                        "error_message": "Cancelled by user"
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"🚫 Cancelled job {job_id[:8]}...")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling job: {e}")
            return False
    
    def get_worker_stats(self) -> List[Dict[str, Any]]:
        """Get statistics about active workers."""
        try:
            pipeline = [
                {"$match": {"worker_id": {"$ne": None}}},
                {"$group": {
                    "_id": "$worker_id",
                    "total_jobs": {"$sum": 1},
                    "completed_jobs": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    },
                    "failed_jobs": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                    },
                    "processing_jobs": {
                        "$sum": {"$cond": [{"$eq": ["$status", "processing"]}, 1, 0]}
                    },
                    "last_activity": {"$max": "$started_at"}
                }},
                {"$sort": {"last_activity": -1}}
            ]
            
            return list(self.jobs_collection.aggregate(pipeline))
            
        except Exception as e:
            logger.error(f"Error getting worker stats: {e}")
            return []
        
    def queue_all_unanalyzed_simple(self, max_cards: int = 0) -> int:
        """
        Simple method to queue ALL unanalyzed cards.
        No complex logic, just get it done.
        
        Args:
            max_cards: Maximum cards to queue (0 = unlimited)
            
        Returns:
            Number of jobs enqueued
        """
        try:
            cards_collection = self.db['cards']
            
            # Simple query: find cards that aren't fully analyzed
            query = {
                "$or": [
                    {"analysis.fully_analyzed": {"$ne": True}},
                    {"analysis": {"$exists": False}}
                ]
            }
            
            # Apply limit if specified
            cursor = cards_collection.find(query)
            if max_cards > 0:
                cursor = cursor.limit(max_cards)
            
            jobs_queued = 0
            
            for card in cursor:                # Skip if job already exists (let the enqueue method handle duplicates)
                job_id = self.enqueue_card_analysis_smart(card['uuid'])
                if job_id:
                    jobs_queued += 1
            
            logger.info(f"🎯 Simple queue: enqueued {jobs_queued} cards")
            return jobs_queued
            
        except Exception as e:
            logger.error(f"Error in simple queue: {e}")
            return 0
    
    def enqueue_card_analysis_smart(self, card_uuid: str, job_type: str = "full_analysis") -> Optional[str]:
        """
        Add a card analysis job with price-based prioritization.
        
        Priority system: Card price * 100 (higher price = higher priority)
        - $100.00 card = priority 10,000
        - $10.50 card = priority 1,050
        - $1.25 card = priority 125
        - $0.50 card = priority 50
        - $0.00 card = priority 0
        
        Args:
            card_uuid: UUID of the card to analyze
            job_type: Type of analysis
            
        Returns:
            Job ID if successful, None if failed
        """
        from .models import get_cards_collection
        
        try:
            # Get card data to determine priority
            cards_collection = get_cards_collection()
            card = cards_collection.find_one(
                {'uuid': card_uuid},
                {
                    'analysis.components': 1, 
                    'edhrecPriorityScore': 1,
                    'prices.usd': 1,
                    'name': 1
                }
            )
            
            if not card:
                logger.warning(f"Card not found for smart prioritization: {card_uuid}")
                return self.enqueue_card_analysis(card_uuid, priority=0, job_type=job_type)
            
            # Calculate smart priority
            priority = self._calculate_smart_priority(card)
            
            # Log priority reasoning
            card_name = card.get('name', 'Unknown')
            if priority >= 1000:
                logger.info(f"🎯 HIGH PRIORITY (Finishing): {card_name} - Priority {priority}")
            elif priority >= 500:
                logger.info(f"⭐ EDHREC Priority: {card_name} - Priority {priority}")
            elif priority >= 50:
                logger.info(f"💰 Price Priority: {card_name} - Priority {priority}")
            else:
                logger.info(f"📋 Standard Priority: {card_name} - Priority {priority}")
            
            return self.enqueue_card_analysis(card_uuid, priority=priority, job_type=job_type)
            
        except Exception as e:
            logger.error(f"Error in smart prioritization for {card_uuid}: {e}")            # Fallback to standard enqueue
            return self.enqueue_card_analysis(card_uuid, priority=0, job_type=job_type)
    
    def _calculate_smart_priority(self, card: Dict[str, Any]) -> int:
        """
        Dead simple priority: Use negative EDHREC rank directly.
        Lower EDHREC rank = higher priority in processing queue.
        MongoDB sorts by priority DESC, so we use negative values.
        """
        try:
            # Get EDHREC ranking
            edhrec_rank = card.get('edhrecRank')
            if edhrec_rank:
                edhrec_rank = int(float(edhrec_rank))
                # Use negative rank so lower ranks get higher priority
                # Rank 1 = priority -1 (highest when sorted DESC)
                # Rank 50,000 = priority -50,000 (lower when sorted DESC)
                return -edhrec_rank
            else:
                return -999999  # No EDHREC data = lowest priority
                
        except (ValueError, TypeError):
            return -999999  # Fallback to lowest priority

# Global job queue instance
job_queue = JobQueue()
