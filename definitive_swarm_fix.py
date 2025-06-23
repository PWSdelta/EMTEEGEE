#!/usr/bin/env python3
"""
DEFINITIVE Enhanced Swarm Manager Fix
This script completely fixes both work assignment AND result submission
"""

def apply_definitive_fix():
    file_path = 'cards/enhanced_swarm_manager.py'
    
    # Read the entire file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Applying DEFINITIVE Enhanced Swarm Manager fix...")
    
    # 1. COMPLETELY REPLACE the get_priority_work_batch method
    old_method_start = "def get_priority_work_batch(self, worker_id: str, max_tasks: int = 1) -> List[Dict[str, Any]]:"
    old_method_end = "return tasks"
    
    new_method = '''def get_priority_work_batch(self, worker_id: str, max_tasks: int = 1) -> List[Dict[str, Any]]:
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
        return tasks'''
    
    # Find the method and replace it completely
    start_idx = content.find(old_method_start)
    if start_idx != -1:
        # Find the end of the method (next def or class declaration)
        search_start = start_idx + len(old_method_start)
        next_method = content.find("\n    def ", search_start)
        next_class = content.find("\n\nclass ", search_start)
        
        # Choose the earliest occurrence
        end_candidates = [idx for idx in [next_method, next_class] if idx != -1]
        if end_candidates:
            end_idx = min(end_candidates)
        else:
            end_idx = len(content)
        
        # Replace the entire method
        content = content[:start_idx] + new_method + content[end_idx:]
        print("✅ 1. Replaced get_priority_work_batch method with EDHREC queue")
    else:
        print("❌ 1. Could not find get_priority_work_batch method")
    
    # 2. Fix the card lookup in submit_enhanced_results
    old_card_lookup = """        card_uuid = task['card_uuid']
        card = self.cards.find_one({'uuid': card_uuid})
        if not card:
            return {'status': 'error', 'message': 'Card not found'}"""
    
    new_card_lookup = """        card_uuid = task['card_uuid']
        # Try to find card by uuid first, then by id
        card = self.cards.find_one({'uuid': card_uuid})
        if not card:
            card = self.cards.find_one({'id': card_uuid})
        if not card:
            enhanced_swarm_logger.error(f"Card not found with uuid/id: {card_uuid}")
            return {'status': 'error', 'message': 'Card not found'}"""
    
    if old_card_lookup in content:
        content = content.replace(old_card_lookup, new_card_lookup)
        print("✅ 2. Fixed card lookup in submit_enhanced_results")
    else:
        print("⚠️  2. Card lookup already fixed or not found")
    
    # 3. Add _create_simple_task method if not present
    if '_create_simple_task' not in content:
        simple_task_method = '''
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
'''
        
        # Insert before submit_enhanced_results method
        submit_method_marker = "def submit_enhanced_results(self, worker_id: str, task_id: str, results: Dict[str, Any]) -> Dict[str, str]:"
        if submit_method_marker in content:
            content = content.replace(submit_method_marker, simple_task_method + "\n    " + submit_method_marker)
            print("✅ 3. Added _create_simple_task method")
        else:
            print("❌ 3. Could not find location to add _create_simple_task method")
    else:
        print("✅ 3. _create_simple_task method already exists")
    
    # Write the completely fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🎯 DEFINITIVE Enhanced Swarm Manager fix applied!")
    print("\n🚀 The system should now:")
    print("  ✅ Use EDHREC queue for work assignment (no more timeouts)")
    print("  ✅ Handle both uuid and id fields in result submission")
    print("  ✅ Successfully process Path of Ancestry, Path to Exile, etc.")
    print("  ✅ Keep GPU busy with continuous analysis tasks")
    print("\n💪 Your 29,249 cards will be processed efficiently!")
    return True

if __name__ == '__main__':
    apply_definitive_fix()
