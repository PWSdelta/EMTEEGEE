"""
Enhanced Swarm Manager with Smart Prioritization and Batch Processing
Implements intelligent card prioritization and batch processing for improved performance
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from bson import ObjectId

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings
from cards.models import get_mongodb_collection
from cards.coherence_manager import coherence_manager
from cards.swarm_logging import get_swarm_logger, enhanced_swarm_logger

class EnhancedSwarmManager:
    """Enhanced swarm manager with smart prioritization and batch processing"""
    
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
    
    # Priority weights for smart queuing
    PRIORITY_WEIGHTS = {
        'edhrec_rank': 0.4,      # Popular cards first
        'market_price': 0.3,     # Expensive cards prioritized  
        'recent_requests': 0.2,  # Recently viewed cards
        'completion_rate': 0.1   # Cards with some analysis
    }
    
    def __init__(self):
        # Use existing MongoDB connection pattern
        self.cards = get_mongodb_collection('cards')
        self.workers = get_mongodb_collection('swarm_workers')
        self.tasks = get_mongodb_collection('swarm_tasks')
        self.priority_cache = get_mongodb_collection('priority_cache')
          # Initialize priority cache
        self._initialize_priority_cache()
        
    def _initialize_priority_cache(self):
        """Initialize or update the priority cache for smart queuing"""
        enhanced_swarm_logger.info("Initializing priority cache...")
        
        # Calculate priority scores for all cards
        cards_cursor = self.cards.find({}, {
            'uuid': 1, 'id': 1, 'name': 1, 'edhrecRank': 1, 'prices': 1,
            'analysis.component_count': 1, 'view_count': 1
        })
        
        priority_updates = []
        for card in cards_cursor:
            priority_score = self._calculate_priority_score(card)
            # Handle both 'uuid' and 'id' fields for card identification
            card_id = card.get('uuid') or card.get('id') or str(card.get('_id'))
            if not card_id:
                enhanced_swarm_logger.error(f"Card missing identification field: {card.get('name', 'Unknown')}")
                continue
            priority_updates.append({
                'card_uuid': card_id,
                'priority_score': priority_score,
                'last_updated': datetime.now(timezone.utc)
            })
        
        # Batch insert priority scores
        if priority_updates:
            self.priority_cache.delete_many({})  # Clear old cache
            self.priority_cache.insert_many(priority_updates)
            enhanced_swarm_logger.priority_cache_updated(len(priority_updates))
    
    def _calculate_priority_score(self, card: Dict[str, Any]) -> float:
        """Calculate smart priority score for a card"""
        score = 0.0
        
        # EDHREC popularity (lower rank = higher priority)
        edhrec_rank = card.get('edhrecRank')
        if edhrec_rank and edhrec_rank > 0:
            # Normalize: cards ranked 1-1000 get highest priority
            edhrec_score = max(0, 1 - (edhrec_rank / 50000))  # Scale 0-1
            score += edhrec_score * self.PRIORITY_WEIGHTS['edhrec_rank']
        
        # Market price (expensive cards prioritized)
        prices = card.get('prices', {})
        usd_price = prices.get('usd', '0')
        try:
            price_value = float(usd_price) if usd_price else 0
            # Normalize: $0-100+ range
            price_score = min(1.0, price_value / 100.0)
            score += price_score * self.PRIORITY_WEIGHTS['market_price']
        except ValueError:
            pass
        
        # Recent view activity
        view_count = card.get('view_count', 0)
        recent_views = card.get('recent_views', 0)
        activity_score = min(1.0, (view_count + recent_views * 5) / 100)
        score += activity_score * self.PRIORITY_WEIGHTS['recent_requests']
        
        # Partial completion bonus (cards with some analysis get priority)
        analysis = card.get('analysis', {})
        component_count = analysis.get('component_count', 0)
        if component_count > 0:
            completion_score = min(1.0, component_count / 10)  # Boost partially complete
            score += completion_score * self.PRIORITY_WEIGHTS['completion_rate']
        
        return score
    
    def get_priority_work_batch(self, worker_id: str, max_tasks: int = 1) -> List[Dict[str, Any]]:
        """Get prioritized work batch using simple EDHREC queue"""
        worker = self.workers.find_one({'worker_id': worker_id})
        if not worker:
            return []
        
        # Update heartbeat
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$set': {'last_heartbeat': datetime.now(timezone.utc)}}
        )
        
        assigned_components = self._get_worker_components(worker['capabilities'])
        
        # Simple EDHREC-based queue: get cards with strongest EDHREC rank first
        enhanced_swarm_logger.info(f"📋 Finding work for {worker_id} with components: {assigned_components}")
        
        cards_needing_work = list(self.cards.find({
            '$or': [
                {'analysis.component_count': {'$lt': 20}},
                {'analysis.component_count': {'$exists': False}}
            ],
            'edhrecRank': {'$exists': True, '$ne': None}
        }, {
            'uuid': 1, 'id': 1, 'name': 1, 'edhrecRank': 1, 'analysis': 1,
            'types': 1, 'subtypes': 1, 'rarity': 1, 'manaValue': 1, 'mana_cost': 1,
            'type_line': 1, 'oracle_text': 1, 'power': 1, 'toughness': 1
        }).sort('edhrecRank', 1).limit(max_tasks * 10))  # Strongest EDHREC rank first
        
        enhanced_swarm_logger.info(f"📊 Found {len(cards_needing_work)} cards needing analysis")
        
        if not cards_needing_work:
            enhanced_swarm_logger.info("✅ No cards need analysis - all work complete!")
            return []
        
        # Convert cards to task format
        tasks = []
        for card in cards_needing_work[:max_tasks]:
            task = self._create_simple_task(card, worker_id, assigned_components)
            if task:
                tasks.append(task)
        
        enhanced_swarm_logger.info(f"🎯 Created {len(tasks)} tasks for worker {worker_id}")
        return tasks
    def _create_smart_batches(self, priority_cards: List[Dict[str, Any]], 
                            assigned_components: List[str], max_batches: int) -> List[List[Dict[str, Any]]]:
        """Create smart batches of related cards for context-aware analysis"""
        
        # Group cards by similarity for batch processing
        card_groups = defaultdict(list)
        
        for priority_card in priority_cards:
            card_data = priority_card['card_data'][0]  # From lookup
            
            # Skip if already fully analyzed
            if card_data.get('analysis', {}).get('fully_analyzed'):
                continue
            
            # Check if this worker can contribute
            existing_components = set()
            if 'analysis' in card_data and 'components' in card_data['analysis']:
                existing_components = set(card_data['analysis']['components'].keys())
            
            missing_components = [comp for comp in assigned_components 
                                if comp not in existing_components]
            if not missing_components:
                continue
            
            # Group by card characteristics for batch processing
            group_key = self._get_batch_group_key(card_data)
            card_groups[group_key].append({
                'card_data': card_data,
                'priority_score': priority_card['priority_score'],
                'missing_components': missing_components
            })
          # Create batches from groups
        batches = []
        for group_key, cards in card_groups.items():
            # Sort by priority within group
            cards.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # Create batch (limit size for performance)
            batch_size = min(5, len(cards))  # Max 5 cards per batch
            batch = cards[:batch_size]
            batches.append(batch)
            
            # Log batch creation
            if batch:
                enhanced_swarm_logger.batch_created(
                    batch_size, group_key, batch[0]['priority_score']
                )
            
            if len(batches) >= max_batches:
                break
        
        return batches
    
    def _get_batch_group_key(self, card_data: Dict[str, Any]) -> str:
        """Generate grouping key for batch processing similar cards"""
        
        # Group by card characteristics for contextual analysis
        type_line = card_data.get('type_line', '')
        mana_cost = card_data.get('mana_cost', '')
        
        # Primary type (Creature, Instant, etc.)
        primary_type = type_line.split()[0] if type_line else 'Unknown'
        
        # Color identity
        colors = []
        if 'W' in mana_cost: colors.append('W')
        if 'U' in mana_cost: colors.append('U') 
        if 'B' in mana_cost: colors.append('B')
        if 'R' in mana_cost: colors.append('R')
        if 'G' in mana_cost: colors.append('G')
        color_identity = ''.join(sorted(colors)) if colors else 'C'
        
        # Rough mana value grouping
        import re
        mana_values = re.findall(r'\\d+', mana_cost)
        total_mana = sum(int(mv) for mv in mana_values) + len([c for c in mana_cost if c in 'WUBRG'])
        mana_group = 'low' if total_mana <= 3 else 'mid' if total_mana <= 6 else 'high'
        
        return f"{primary_type}_{color_identity}_{mana_group}"
    
    def _create_batch_task(self, batch: List[Dict[str, Any]], worker_id: str, 
                          assigned_components: List[str]) -> Optional[Dict[str, Any]]:
        """Create a batch task for multiple related cards"""
        
        if not batch:
            return None
        
        # Select primary card (highest priority) and context cards
        primary_card = batch[0]
        context_cards = batch[1:] if len(batch) > 1 else []
        
        # Find components to generate for the primary card
        missing_components = primary_card['missing_components']
        
        # Limit components per task for performance
        components_to_generate = missing_components[:3]
        
        task_id = str(uuid.uuid4())
        task = {
            'task_id': task_id,
            'card_id': str(primary_card['card_data']['_id']),
            'card_uuid': primary_card['card_data']['uuid'],
            'card_name': primary_card['card_data'].get('name', 'Unknown'),
            'components': components_to_generate,
            'batch_context': [
                {
                    'name': card['card_data'].get('name'),
                    'type': card['card_data'].get('type_line'),
                    'text': card['card_data'].get('oracle_text', '')[:200]  # Truncated for context
                } 
                for card in context_cards
            ],
            'priority_score': primary_card['priority_score'],
            'assigned_to': worker_id,
            'created_at': datetime.now(timezone.utc),
            'status': 'assigned',
            'batch_processing': True,
            'card_data': {
                'name': primary_card['card_data'].get('name'),
                'mana_cost': primary_card['card_data'].get('mana_cost'),
                'type_line': primary_card['card_data'].get('type_line'),
                'oracle_text': primary_card['card_data'].get('oracle_text'),
                'power': primary_card['card_data'].get('power'),
                'toughness': primary_card['card_data'].get('toughness')
            }
        }
        
        # Store task
        self.tasks.insert_one(task)
        return task
    
    
    def _create_simple_task(self, card: Dict[str, Any], worker_id: str, 
                           assigned_components: List[str]) -> Optional[Dict[str, Any]]:
        """Create a simple task for a single card using EDHREC queue approach"""
        
        # Handle both uuid and id fields
        card_uuid = card.get('uuid') or card.get('id') or str(card.get('_id'))
        if not card_uuid:
            enhanced_swarm_logger.error(f"Card missing identification field: {card.get('name', 'Unknown')}")
            return None
        
        # Determine what components are missing
        existing_components = card.get('analysis', {}).get('components', {})
        current_count = len(existing_components)
        
        # Find components that need to be generated
        missing_components = []
        for component in assigned_components:
            if component not in existing_components:
                missing_components.append(component)
        
        # Limit to 3 components per task for performance
        components_to_generate = missing_components[:3]
        
        if not components_to_generate:
            enhanced_swarm_logger.debug(f"No components needed for card: {card.get('name')}")
            return None
        
        task_id = str(uuid.uuid4())
        task = {
            'task_id': task_id,
            'card_id': str(card.get('_id')),
            'card_uuid': card_uuid,
            'card_name': card.get('name', 'Unknown'),
            'components': components_to_generate,
            'edhrec_rank': card.get('edhrecRank', 999999),
            'current_component_count': current_count,
            'assigned_to': worker_id,
            'created_at': datetime.now(timezone.utc),
            'status': 'assigned',
            'batch_processing': False,
            'card_data': {
                'name': card.get('name'),
                'mana_cost': card.get('mana_cost'),
                'type_line': card.get('type_line'),
                'oracle_text': card.get('oracle_text'),
                'power': card.get('power'),
                'toughness': card.get('toughness'),
                'rarity': card.get('rarity'),
                'edhrec_rank': card.get('edhrecRank')
            }
        }
        
        # Store task
        self.tasks.insert_one(task)
        enhanced_swarm_logger.info(f"📝 Created task {task_id} for {card.get('name')} (EDHREC: {card.get('edhrecRank', 'N/A')})")
        return task

    def submit_enhanced_results(self, worker_id: str, task_id: str, results: Dict[str, Any]) -> Dict[str, str]:
        """Submit results with coherence validation"""
        
        task = self.tasks.find_one({'task_id': task_id})
        if not task:
            return {'status': 'error', 'message': 'Task not found'}
        
        if task['assigned_to'] != worker_id:
            return {'status': 'error', 'message': 'Task not assigned to this worker'}
        
        card_uuid = task['card_uuid']
        # Try to find card by uuid first, then by id
        card = self.cards.find_one({'uuid': card_uuid})
        if not card:
            card = self.cards.find_one({'id': card_uuid})
        if not card:
            enhanced_swarm_logger.error(f"Card not found with uuid/id: {card_uuid}")
            return {'status': 'error', 'message': 'Card not found'}
          # Get existing analysis for coherence checking
        existing_components = {}
        if 'analysis' in card and 'components' in card['analysis']:
            existing_components = card['analysis']['components']
          # Validate coherence for each new component
        validated_components = {}
        coherence_warnings = []
        
        for component_type, content in results.get('components', {}).items():
            # Check coherence with existing analysis
            coherence_result = coherence_manager.validate_component_coherence(
                component_type, content, existing_components
            )
            
            if not coherence_result['is_coherent']:
                coherence_warning = {
                    'component': component_type,
                    'conflicts': coherence_result['potential_conflicts'],
                    'suggestions': coherence_result['suggestions']
                }
                coherence_warnings.append(coherence_warning)
                
                # Log coherence warning
                enhanced_swarm_logger.coherence_warning(
                    component_type, coherence_result['potential_conflicts']
                )
            
            # Store component with coherence metadata
            validated_components[f'analysis.components.{component_type}'] = {
                'content': content,
                'generated_at': datetime.now(timezone.utc),
                'generated_by': worker_id,
                'model_info': results.get('model_info', {}),
                'coherence_score': coherence_result['confidence_score'],
                'batch_processed': task.get('batch_processing', False)
            }
        
        # Update card with new analysis
        from bson import ObjectId
        self.cards.update_one(
            {'_id': ObjectId(task['card_id'])},
            {
                '$set': validated_components,
                '$inc': {'analysis.component_count': len(results.get('components', {}))},
                '$currentDate': {'analysis.last_updated': True}
            }
        )
        
        # Check if card is now fully analyzed
        updated_card = self.cards.find_one({'_id': ObjectId(task['card_id'])})
        if updated_card and 'analysis' in updated_card and 'components' in updated_card['analysis']:
            all_components = set(self.GPU_COMPONENTS + self.CPU_HEAVY_COMPONENTS + self.BALANCED_COMPONENTS)
            existing_components = set(updated_card['analysis']['components'].keys())
            
            if existing_components >= all_components:
                self.cards.update_one(
                    {'_id': ObjectId(task['card_id'])},
                    {'$set': {'analysis.fully_analyzed': True}}
                )
        
        # Mark task as completed
        self.tasks.update_one(
            {'task_id': task_id},
            {
                '$set': {
                    'status': 'completed',
                    'completed_at': datetime.now(timezone.utc),
                    'execution_time': results.get('execution_time', 0),
                    'coherence_warnings': coherence_warnings
                }
            }
        )
        
        # Update worker stats
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$inc': {'tasks_completed': 1}}
        )
          # Update priority cache for this card (may have changed)
        priority_score = self._calculate_priority_score(updated_card)
        self.priority_cache.update_one(
            {'card_uuid': card_uuid},
            {'$set': {'priority_score': priority_score, 'last_updated': datetime.now(timezone.utc)}},
            upsert=True
        )
        
        # Log task completion
        execution_time = results.get('execution_time', 0)
        card_name = task.get('card_name', 'Unknown')
        enhanced_swarm_logger.task_completed(
            task_id, card_name, execution_time, len(coherence_warnings)
        )
        
        response = {'status': 'success', 'message': f'Task {task_id} completed'}
        if coherence_warnings:
            response['coherence_warnings'] = coherence_warnings
        
        return response
    
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
    
    def register_worker(self, worker_id: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new worker node"""
        worker_info = {
            'worker_id': worker_id,
            'capabilities': capabilities,
            'registered_at': datetime.now(timezone.utc),
            'last_heartbeat': datetime.now(timezone.utc),
            'status': 'active',
            'tasks_completed': 0,            'tasks_failed': 0,
            'average_time_per_task': None
        }
        
        self.workers.update_one(
            {'worker_id': worker_id},
            {'$set': worker_info},
            upsert=True
        )
          # Log worker registration
        enhanced_swarm_logger.worker_registered(worker_id, capabilities)
        
        return {
            'status': 'registered',
            'worker_id': worker_id,
            'assigned_components': self._get_worker_components(capabilities)
        }
    
    def get_enhanced_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status with priority queue info"""
        try:
            total_workers = self.workers.count_documents({'status': 'active'})
            active_workers = self.workers.count_documents({
                'status': 'active',
                'last_heartbeat': {'$gte': datetime.now(timezone.utc) - timedelta(minutes=5)}
            })
            
            pending_tasks = self.tasks.count_documents({'status': 'assigned'})
            completed_tasks = self.tasks.count_documents({'status': 'completed'})
            
            total_cards = self.cards.count_documents({})            # Count analyzed cards using comprehensive criteria
            # This catches all cards with ANY analysis components from both legacy and new formats
            analyzed_cards = self.cards.count_documents({
                '$or': [
                    {'analysis.components': {'$exists': True, '$ne': {}}},  # Cards with analysis components
                    {'analysis.component_count': {'$gt': 0}},  # Cards with component count > 0  
                    {'analysis.fully_analyzed': True},  # Fully analyzed cards
                    {'analysis.analysis_completed_at': {'$exists': True, '$ne': None}},  # Legacy completed
                    {'fully_analyzed': True},  # Legacy fully_analyzed field
                    {'analysis_completed_at': {'$exists': True, '$ne': None}}  # Legacy analysis_completed_at
                ]
            })
            
            # Priority queue stats
            high_priority_pending = self.priority_cache.count_documents({
                'priority_score': {'$gte': 0.7}
            })
            
            status = {
                'workers': {
                    'total': total_workers,
                    'active': active_workers,
                    'offline': total_workers - active_workers
                },
                'tasks': {
                    'pending': pending_tasks,
                    'completed': completed_tasks
                },
                'cards': {
                    'total': total_cards,
                    'analyzed': analyzed_cards,
                    'completion_rate': f"{(analyzed_cards/total_cards)*100:.1f}%" if total_cards > 0 else "0%",
                    'high_priority_pending': high_priority_pending
                },
                'enhancements': {
                    'smart_prioritization': True,
                    'batch_processing': True,
                    'coherence_validation': True
                }
            }
            
            # Log stats periodically
            enhanced_swarm_logger.stats(
                workers_active=active_workers,
                tasks_pending=pending_tasks,
                tasks_completed=completed_tasks,
                cards_analyzed=analyzed_cards,
                completion_rate=f"{(analyzed_cards/total_cards)*100:.1f}%" if total_cards > 0 else "0%"
            )
            
            return status
            
        except Exception as e:
            enhanced_swarm_logger.error(f"Failed to get swarm status: {str(e)}")
            return {                'error': str(e),
                'workers': {'total': 0, 'active': 0, 'offline': 0},
                'tasks': {'pending': 0, 'completed': 0},
                'cards': {'total': 0, 'analyzed': 0, 'completion_rate': '0%'}
            }

    def get_work(self, worker_id: str) -> List[Dict[str, Any]]:
        """RANDOM SELECTION: Get a random unanalyzed card with ALL 20 components"""
        try:
            enhanced_swarm_logger.info(f"🔄 Getting random work for worker {worker_id}")
            
            # Update worker heartbeat
            self.workers.update_one(
                {'worker_id': worker_id},
                {'$set': {'last_heartbeat': datetime.now(timezone.utc)}}
            )
            
            # Get ALL 20 components (fixed list)
            all_components = (
                self.GPU_COMPONENTS + 
                self.CPU_HEAVY_COMPONENTS + 
                self.BALANCED_COMPONENTS
            )
            
            # Find a RANDOM card that needs analysis using MongoDB $sample
            pipeline = [
                {
                    '$match': {
                        '$or': [
                            {'analysis.component_count': {'$exists': False}},  # No analysis
                            {'analysis.component_count': {'$lt': 20}},  # Incomplete analysis
                            {'analysis.fully_analyzed': {'$ne': True}}  # Not marked complete
                        ]
                    }
                },
                {'$sample': {'size': 1}}  # RANDOM SELECTION!
            ]
            
            random_cards = list(self.cards.aggregate(pipeline))
            
            if not random_cards:
                enhanced_swarm_logger.info("✅ No cards need analysis - all work complete!")
                return []
            
            card = random_cards[0]
            card_name = card.get('name', 'Unknown')
            card_uuid = card.get('uuid', str(card['_id']))
            
            enhanced_swarm_logger.info(f"� RANDOM: Assigning {card_name} to worker {worker_id}")
            
            # Create ONE task with ALL 20 components
            task_id = str(uuid.uuid4())
            task = {
                'task_id': task_id,
                'card_id': str(card['_id']),
                'card_uuid': card_uuid,
                'card_name': card_name,
                'components': all_components,  # ALL 20 COMPONENTS
                'assigned_to': worker_id,
                'created_at': datetime.now(timezone.utc),
                'status': 'assigned',
                'card_data': {
                    'name': card.get('name'),
                    'mana_cost': card.get('mana_cost'),
                    'type_line': card.get('type_line'),
                    'oracle_text': card.get('oracle_text'),
                    'power': card.get('power'),
                    'toughness': card.get('toughness'),
                    'edhrecRank': card.get('edhrecRank')
                }            }
            
            # Store the assignment
            self.tasks.insert_one(task)
            
            enhanced_swarm_logger.info(f"✅ RANDOM assignment: {card_name} with {len(all_components)} components to {worker_id}")
            return [task]
            
        except Exception as e:
            enhanced_swarm_logger.error(f"❌ Random work assignment failed for worker {worker_id}: {str(e)}")
            import traceback
            enhanced_swarm_logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def submit_task_result(self, task_id: str, worker_id: str, card_id: str, results: Dict[str, Any]) -> bool:
        """Submit task results with robust card lookup"""
        try:
            enhanced_swarm_logger.info(f"📥 Receiving results from worker {worker_id} for card {card_id}")
            
            # Find the task
            task = self.tasks.find_one({'task_id': task_id})
            if not task:
                enhanced_swarm_logger.error(f"❌ Task {task_id} not found")
                return False
            
            # Find the card using multiple lookup methods
            card = None
            
            # Method 1: Try by uuid
            if card_id:
                card = self.cards.find_one({'uuid': card_id})
            
            # Method 2: Try by MongoDB _id
            if not card:
                try:
                    from bson import ObjectId
                    card = self.cards.find_one({'_id': ObjectId(card_id)})
                except:
                    pass
            
            # Method 3: Try by task's card_uuid
            if not card and 'card_uuid' in task:
                card = self.cards.find_one({'uuid': task['card_uuid']})
            
            # Method 4: Try by task's card_id  
            if not card and 'card_id' in task:
                try:
                    from bson import ObjectId
                    card = self.cards.find_one({'_id': ObjectId(task['card_id'])})
                except:
                    pass
            
            # Method 5: Last resort - find by name
            if not card and 'card_name' in task:
                card = self.cards.find_one({'name': task['card_name']})
            
            if not card:
                enhanced_swarm_logger.error(f"❌ Card not found for task {task_id}")
                return False
            
            enhanced_swarm_logger.info(f"✅ Found card {card.get('name')} for result submission")
              # Update card with new analysis
            analysis_update = {}
            component_count = 0
            
            if 'results' in results and isinstance(results['results'], dict):
                for component_type, content in results['results'].items():
                    if content and content != 'placeholder':  # Skip placeholder content
                        analysis_update[f'analysis.components.{component_type}'] = {
                            'content': content,
                            'generated_at': datetime.now(timezone.utc),
                            'generated_by': worker_id,
                            'coherence_score': 0.8  # Default coherence score
                        }
                        component_count += 1
            
            # Calculate total components after update
            existing_components = card.get('analysis', {}).get('components', {})
            total_components_after = len(existing_components) + component_count
            
            # Prepare card update
            card_update = {
                '$set': analysis_update,
                '$inc': {'analysis.component_count': component_count},
                '$currentDate': {'analysis.last_updated': True}
            }
            
            # If we now have 20 components, mark as fully analyzed
            if total_components_after >= 20:
                card_update['$set']['analysis.fully_analyzed'] = True
                card_update['$set']['analysis.analysis_completed_at'] = datetime.now(timezone.utc)
                enhanced_swarm_logger.info(f"🎉 Card {card.get('name')} is now FULLY ANALYZED with {total_components_after} components!")
            
            if analysis_update:
                self.cards.update_one({'_id': card['_id']}, card_update)
                enhanced_swarm_logger.info(f"📊 Updated {card.get('name')} with {component_count} new components (total: {total_components_after})")
            else:
                enhanced_swarm_logger.warning(f"⚠️ No valid analysis content received for {card.get('name')}")
            
            # Mark task as completed
            self.tasks.update_one(
                {'task_id': task_id},
                {
                    '$set': {
                        'status': 'completed',
                        'completed_at': datetime.now(timezone.utc)
                    }
                }
            )
            
            # Update worker stats
            self.workers.update_one(
                {'worker_id': worker_id},
                {'$inc': {'tasks_completed': 1}}
            )
            
            enhanced_swarm_logger.info(f"✅ Results processed successfully for card {card.get('name')}")
            return True
            
        except Exception as e:
            enhanced_swarm_logger.error(f"❌ Submit task result failed: {str(e)}")
            return False

# Global instance
enhanced_swarm = EnhancedSwarmManager()

if __name__ == "__main__":
    enhanced_swarm_logger.info("Enhanced Swarm Manager initialized")
    status = enhanced_swarm.get_enhanced_swarm_status()
    enhanced_swarm_logger.info(f"Current status: {json.dumps(status, indent=2, default=str)}")
