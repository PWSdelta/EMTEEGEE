#!/usr/bin/env python3
"""
SUPER SIMPLE Enhanced Swarm Manager - Instant Work Assignment
=============================================================

Philosophy: Load once, pop instantly.

1. Startup: Load all unanalyzed cards into a simple in-memory queue (sorted by priority)
2. Worker asks for work: Pop one card from front of queue and return it
3. Worker processes and submits results
4. Repeat

No complex queries during work assignment = INSTANT response!
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from collections import deque
import threading

from .swarm_logging import get_swarm_logger

# Simple MongoDB connection
from pymongo import MongoClient

def get_mongodb_collection(collection_name):
    """Simple MongoDB connection"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emteegee_dev']  # CORRECT DATABASE NAME!
    return db[f'cards_{collection_name}']

logger = get_swarm_logger('SIMPLE_SWARM')

class SimpleSwarmManager:
    """Dead simple swarm manager with instant work assignment"""
    
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['emteegee_dev']
        self.cards = db['cards']  # Use correct collection name
        self.workers = get_mongodb_collection('workers')
        self.tasks = get_mongodb_collection('tasks')
        
        # Simple in-memory work queue - thread-safe
        self.work_queue = deque()
        self.queue_lock = threading.Lock()
        
        # Load the queue at startup
        self._load_work_queue()
        
        logger.info(f"🚀 Simple Swarm Manager initialized with {len(self.work_queue)} cards ready for work")
      def _load_work_queue(self):
        """Load all unanalyzed card IDs into work queue, sorted by priority"""
        logger.info("📥 Loading work queue...")
        
        # Get only card IDs and minimal data for unanalyzed cards
        unanalyzed_cards = list(self.cards.find({
            'analysis.fully_analyzed': {'$ne': True}
        }, {
            '_id': 1,           # Only get the ID
            'name': 1,          # And name for display
            'edhrecRank': 1     # And EDHREC rank for sorting
        }))
        
        # Sort by priority (EDHREC rank = lower number = higher priority)
        def get_priority_score(card):
            # Simple priority: EDHREC rank (lower = better)
            edhrec_rank = card.get('edhrecRank', 999999)
            if edhrec_rank and edhrec_rank > 0:
                return edhrec_rank
            return 999999
        
        sorted_cards = sorted(unanalyzed_cards, key=get_priority_score)
        
        # Add to work queue
        with self.queue_lock:
            self.work_queue.clear()
            for card in sorted_cards:
                self.work_queue.append(card)
        
        logger.info(f"✅ Work queue loaded with {len(self.work_queue)} cards")
    
    def get_work_instant(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get work assignment INSTANTLY - just pop from queue"""
        with self.queue_lock:
            if not self.work_queue:
                return None
            
            # Pop one card from front of queue
            card = self.work_queue.popleft()
        
        # Create simple task
        task = {
            'task_id': str(uuid.uuid4()),
            'card_id': str(card['_id']),
            'card_name': card.get('name', 'Unknown'),
            'card_uuid': card.get('uuid', ''),
            'components': ['pricing', 'legality', 'gameplay'],  # Simple components
            'assigned_to': worker_id,
            'assigned_at': datetime.now(timezone.utc).isoformat()        }
        
        logger.info(f"⚡ INSTANT work assignment: {card.get('name')} -> {worker_id}")
        return task
    
    def register_worker(self, worker_id: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Register a worker - FAST version with in-memory cache"""
        # Just cache in memory - skip slow MongoDB for now
        self.worker_cache = getattr(self, 'worker_cache', {})
        self.worker_cache[worker_id] = {
            'capabilities': capabilities,
            'registered_at': datetime.now(timezone.utc),
            'status': 'active'
        }
        
        logger.info(f"⚡ INSTANT worker registration: {worker_id}")
        return {
            'status': 'success',
            'message': f'Worker {worker_id} registered instantly',
            'worker_id': worker_id,
            'queue_size': len(self.work_queue)
        }
    
    def submit_results(self, worker_id: str, card_id: str, results: Dict[str, Any]) -> bool:
        """Submit completed work results"""
        try:
            # Update card with results
            for component_type, component_data in results.items():
                update_data = {
                    f'analysis.components.{component_type}': {
                        'content': component_data,
                        'generated_at': datetime.now(timezone.utc).isoformat(),
                        'worker_id': worker_id
                    }
                }
                
                self.cards.update_one(
                    {'_id': card_id},
                    {'$set': update_data}
                )
            
            logger.info(f"✅ Results submitted: {card_id} by {worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Submit results failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get simple status"""
        with self.queue_lock:
            queue_size = len(self.work_queue)
        
        return {
            'queue_size': queue_size,
            'total_workers': self.workers.count_documents({}),
            'active_workers': self.workers.count_documents({'status': 'active'}),
            'system': 'simple_instant_swarm'
        }

# Global instance
simple_swarm = SimpleSwarmManager()
