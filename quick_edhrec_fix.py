#!/usr/bin/env python3
"""
Quick EDHREC Queue Fix for Enhanced Swarm Manager
This script directly replaces the hanging aggregation with simple EDHREC sorting
"""

def apply_edhrec_queue_fix():
    file_path = 'cards/enhanced_swarm_manager.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic aggregation pipeline
    old_aggregation = '''        # Get high-priority cards needing analysis
        priority_cards = list(self.priority_cache.aggregate([
            {
                '$lookup': {
                    'from': 'cards',
                    'localField': 'card_uuid',
                    'foreignField': 'uuid', 
                    'as': 'card_data'
                }
            },
            {
                '$match': {
                    'card_data': {'$ne': []},
                    'card_data.analysis.fully_analyzed': {'$ne': True}
                }
            },
            {
                '$sort': {'priority_score': -1}  # Highest priority first
            },
            {
                '$limit': max_tasks * 50  # Get extra to filter from
            }
        ]))
        
        # Group related cards for batch processing
        batches = self._create_smart_batches(priority_cards, assigned_components, max_tasks)
        
        # Convert to task format
        tasks = []
        for batch in batches[:max_tasks]:
            task = self._create_batch_task(batch, worker_id, assigned_components)
            if task:
                tasks.append(task)'''
    
    new_edhrec_queue = '''        # Simple EDHREC-based queue: get cards with strongest EDHREC rank first
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
        
        enhanced_swarm_logger.info(f"🎯 Created {len(tasks)} tasks for worker {worker_id}")'''
    
    if old_aggregation in content:
        content = content.replace(old_aggregation, new_edhrec_queue)
        print("✅ Replaced aggregation pipeline with EDHREC queue")
    else:
        print("❌ Could not find aggregation pipeline to replace")
        return False
    
    # Add the _create_simple_task method
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
    if 'def submit_enhanced_results(self, worker_id: str, task_id: str, results: Dict[str, Any]) -> Dict[str, str]:' in content:
        content = content.replace(
            'def submit_enhanced_results(self, worker_id: str, task_id: str, results: Dict[str, Any]) -> Dict[str, str]:',
            simple_task_method + '\n    def submit_enhanced_results(self, worker_id: str, task_id: str, results: Dict[str, Any]) -> Dict[str, str]:'
        )
        print("✅ Added _create_simple_task method")
    else:
        print("❌ Could not find location to add _create_simple_task method")
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🎯 EDHREC queue fix applied successfully!")
    return True

if __name__ == '__main__':
    apply_edhrec_queue_fix()
