#!/usr/bin/env python3
"""
Simplified AI Analysis Swarm Manager
Handles distributed work assignment and result collection
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings
from cards.models import get_mongodb_collection

class SwarmManager:
    """Simplified swarm manager for distributed AI analysis"""
    
    # Component assignment by hardware capability
    GPU_COMPONENTS = [
        'play_tips', 'mulligan_considerations', 'rules_clarifications',
        'combo_suggestions', 'format_analysis', 'synergy_analysis',
        'competitive_analysis', 'tactical_analysis'
    ]
    
    CPU_HEAVY_COMPONENTS = [
        'thematic_analysis', 'historical_context', 'art_flavor_analysis',
        'design_philosophy', 'advanced_interactions', 'meta_positioning'
    ]
    
    BALANCED_COMPONENTS = [
        'budget_alternatives', 'deck_archetypes', 'new_player_guide',
        'sideboard_guide', 'power_level_assessment', 'investment_outlook'
    ]
    
    def __init__(self):
        # Use existing MongoDB connection pattern
        self.cards = get_mongodb_collection('cards')
        self.workers = get_mongodb_collection('swarm_workers')
        self.tasks = get_mongodb_collection('swarm_tasks')
        
    def register_worker(self, worker_id: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new worker node"""
        worker_info = {
            'worker_id': worker_id,
            'capabilities': capabilities,            'registered_at': datetime.now(timezone.utc),
            'last_heartbeat': datetime.now(timezone.utc),
            'status': 'active',
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_time_per_task': None
        }
        
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$set': worker_info},
            upsert=True
        )
        
        return {
            'status': 'registered',
            'worker_id': worker_id,
            'assigned_components': self._get_worker_components(capabilities)
        }
    
    def _get_worker_components(self, capabilities: Dict[str, Any]) -> List[str]:
        """Determine which components a worker should handle"""
        gpu_capable = capabilities.get('gpu_available', False)
        ram_gb = capabilities.get('ram_gb', 8)
        
        assigned = []
        
        # High-end GPU systems get fast components
        if gpu_capable and ram_gb >= 32:
            assigned.extend(self.GPU_COMPONENTS)
        
        # High-RAM systems get CPU-intensive components
        if ram_gb >= 64:
            assigned.extend(self.CPU_HEAVY_COMPONENTS)
        
        # All systems can handle balanced components
        assigned.extend(self.BALANCED_COMPONENTS)
        
        return list(set(assigned))  # Remove duplicates
    def get_work(self, worker_id: str, max_tasks: int = 1) -> List[Dict[str, Any]]:
        """Get work assignments - simple approach: find random card that needs work"""
        worker = self.workers.find_one({'worker_id': worker_id})
        if not worker:
            return []
        
        # Update heartbeat
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$set': {'last_heartbeat': datetime.now(timezone.utc)}}
        )
        
        assigned_components = self._get_worker_components(worker['capabilities'])
          # Simple: Find a random card that doesn't have all components yet
        cards_needing_work = list(self.cards.aggregate([
            {
                '$match': {
                    '$or': [
                        {'analysis.components': {'$exists': False}},
                        {'analysis.fully_analyzed': {'$ne': True}}
                    ]
                }
            },
            {
                '$addFields': {
                    'component_count': {
                        '$cond': {
                            'if': {'$exists': ['$analysis.components', True]},
                            'then': {'$size': {'$objectToArray': '$analysis.components'}},
                            'else': 0
                        }
                    }
                }
            },
            {
                '$match': {
                    'component_count': {'$lt': 20}
                }
            },
            {'$sample': {'size': max_tasks}}  # Get random cards
        ]))
        
        tasks = []
        for card in cards_needing_work:
            # Find missing components this worker can handle
            existing_components = set()
            if 'analysis' in card and 'components' in card['analysis']:
                existing_components = set(card['analysis']['components'].keys())
            
            missing_components = []
            for component in assigned_components:
                if component not in existing_components:
                    missing_components.append(component)
            
            if missing_components:
                # Return card data directly - no task queue needed
                task = {
                    'task_id': str(uuid.uuid4()),  # Just for tracking this session
                    'card_id': str(card['_id']),
                    'card_name': card.get('name', 'Unknown'),
                    'components': missing_components[:3],  # Limit per task
                    'card_data': card
                }
                tasks.append(task)
        
        return tasks
    
    def submit_results(self, task_id: str, worker_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Submit completed analysis results - simple approach: just update the card"""
        # We need the card_id to be passed in the request data
        # For now, this will be handled in the API layer
        
        return {'status': 'success', 'message': f'Task {task_id} completed'}
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get overall swarm system status"""
        try:
            total_workers = self.workers.count_documents({'status': 'active'})
            active_workers = self.workers.count_documents({
                'status': 'active',
                'last_heartbeat': {'$gte': datetime.now(timezone.utc) - timedelta(minutes=5)}
            })
            
            pending_tasks = self.tasks.count_documents({'status': 'assigned'})
            completed_tasks = self.tasks.count_documents({'status': 'completed'})
            
            total_cards = self.cards.count_documents({})
            analyzed_cards = self.cards.count_documents({'analysis.fully_analyzed': True})
            
            return {
                'workers': {
                    'total': total_workers,
                    'active': active_workers,
                    'offline': total_workers - active_workers
                },
                'tasks': {
                    'pending': pending_tasks,
                    'completed': completed_tasks
                },
                'analysis': {
                    'total_cards': total_cards,
                    'analyzed_cards': analyzed_cards,
                    'progress_percentage': (analyzed_cards / total_cards * 100) if total_cards > 0 else 0
                }            }
        except Exception as e:
            return {
                'error': str(e),
                'workers': {'total': 0, 'active': 0, 'offline': 0},
                'tasks': {'pending': 0, 'completed': 0},
                'analysis': {'total_cards': 0, 'analyzed_cards': 0, 'progress_percentage': 0}
            }
