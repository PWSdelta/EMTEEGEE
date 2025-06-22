#!/usr/bin/env python3
"""
AI Analysis Swarm Manager
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
from pymongo import MongoClient
import redis

class SwarmManager:
    """Manages distributed AI analysis work across multiple machines"""
    
    # Component assignment by hardware capability    GPU_COMPONENTS = [
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
        # Use the same MongoDB connection pattern as the models
        mongodb_settings = settings.MONGODB_SETTINGS
        
        # Handle both connection string and legacy settings
        if 'connection_string' in mongodb_settings:
            # Use connection string method
            self.mongo_client = MongoClient(mongodb_settings['connection_string'])
        else:
            # Use legacy host-based method
            if mongodb_settings.get('username') and mongodb_settings.get('password'):
                self.mongo_client = MongoClient(
                    host=mongodb_settings['host'],
                    username=mongodb_settings['username'],
                    password=mongodb_settings['password'],
                    authSource=mongodb_settings.get('auth_source', 'admin')
                )
            else:
                self.mongo_client = MongoClient(mongodb_settings['host'])
        
        db_name = mongodb_settings.get('db_name', 'emteegee_dev')
        self.db = self.mongo_client[db_name]
        self.cards = self.db.cards
        self.workers = self.db.swarm_workers
        self.tasks = self.db.swarm_tasks
          # Redis for real-time queues
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.redis_available = True
        except Exception:
            self.redis_available = False
            print("Redis not available - using MongoDB only")
    
    def register_worker(self, worker_id: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new worker node"""
        worker_info = {
            'worker_id': worker_id,
            'capabilities': capabilities,
            'registered_at': datetime.now(timezone.utc),
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
        cpu_cores = capabilities.get('cpu_cores', 4)
        
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
        """Get work assignments for a specific worker"""
        worker = self.workers.find_one({'worker_id': worker_id})
        if not worker:
            return []
          # Update heartbeat
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$set': {'last_heartbeat': datetime.now(timezone.utc)}}
        )
        
        assigned_components = self._get_worker_components(worker['capabilities'])
        
        # Find cards that need analysis for this worker's components
        tasks = []
        cards_needing_work = self.cards.find({
            '$or': [
                {'analysis.fully_analyzed': {'$ne': True}},
                {'analysis.components': {'$exists': False}}
            ]
        }).limit(max_tasks * 10)  # Get more to filter from
        
        for card in cards_needing_work:
            if len(tasks) >= max_tasks:
                break
                
            card_id = str(card['_id'])
            existing_components = set()
            
            if 'analysis' in card and 'components' in card['analysis']:
                existing_components = set(card['analysis']['components'].keys())
            
            # Find missing components this worker can handle
            missing_components = []
            for component in assigned_components:
                if component not in existing_components:
                    missing_components.append(component)
            
            if missing_components:
                task_id = str(uuid.uuid4())
                task = {
                    'task_id': task_id,
                    'card_id': card_id,
                    'card_name': card.get('name', 'Unknown'),
                    'components': missing_components[:3],  # Limit per task
                    'assigned_to': worker_id,
                    'created_at': datetime.utcnow(),
                    'status': 'assigned',
                    'card_data': {
                        'name': card.get('name'),
                        'mana_cost': card.get('mana_cost'),
                        'type_line': card.get('type_line'),
                        'oracle_text': card.get('oracle_text'),
                        'power': card.get('power'),
                        'toughness': card.get('toughness')
                    }
                }
                
                # Store task
                self.tasks.insert_one(task)
                tasks.append(task)
        
        return tasks
    
    def submit_results(self, worker_id: str, task_id: str, results: Dict[str, Any]) -> Dict[str, str]:
        """Accept completed work from a worker"""
        task = self.tasks.find_one({'task_id': task_id})
        if not task:
            return {'status': 'error', 'message': 'Task not found'}
        
        if task['assigned_to'] != worker_id:
            return {'status': 'error', 'message': 'Task not assigned to this worker'}
        
        # Update the card with new analysis components
        card_id = task['card_id']
        
        # Prepare component updates
        component_updates = {}
        for component_type, content in results.get('components', {}).items():
            component_updates[f'analysis.components.{component_type}'] = {
                'content': content,
                'generated_at': datetime.utcnow(),
                'generated_by': worker_id,
                'model_info': results.get('model_info', {})
            }
        
        # Update card
        update_result = self.cards.update_one(
            {'_id': task['card_id']},
            {
                '$set': component_updates,
                '$inc': {'analysis.component_count': len(results.get('components', {}))},
                '$currentDate': {'analysis.last_updated': True}
            }
        )
        
        # Mark task as completed
        self.tasks.update_one(
            {'task_id': task_id},
            {
                '$set': {
                    'status': 'completed',
                    'completed_at': datetime.utcnow(),
                    'execution_time': results.get('execution_time', 0)
                }
            }
        )
          # Update worker stats
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$inc': {'tasks_completed': 1}}
        )
        
        return {'status': 'success', 'message': f'Task {task_id} completed'}
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get overall swarm system status"""
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
                'active': active_workers
            },
            'tasks': {
                'pending': pending_tasks,
                'completed': completed_tasks
            },
            'cards': {
                'total': total_cards,
                'analyzed': analyzed_cards,
                'completion_rate': f"{(analyzed_cards/total_cards)*100:.1f}%" if total_cards > 0 else "0%"
            }
        }

if __name__ == "__main__":
    manager = SwarmManager()
    print("Swarm Manager initialized")
    print(json.dumps(manager.get_swarm_status(), indent=2, default=str))
