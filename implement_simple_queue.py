#!/usr/bin/env python3
"""
Simple EDHREC Queue Implementation
Replaces complex aggregation with simple EDHREC rank sorting
"""

import re

def implement_simple_edhrec_queue():
    file_path = 'cards/enhanced_swarm_manager.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the complex get_priority_work_batch method
    # Look for the method definition
    method_start = content.find('def get_priority_work_batch(self, worker_id, max_tasks=5):')
    if method_start == -1:
        print("❌ Could not find get_priority_work_batch method")
        return False
    
    # Find the end of the method (next method or class end)
    lines = content[method_start:].split('\n')
    method_lines = []
    indent_level = None
    
    for i, line in enumerate(lines):
        if i == 0:  # First line is the def
            method_lines.append(line)
            continue
            
        # Determine base indent level from first non-empty line after def
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
        
        # If we hit a line with same or less indentation than base method, we're done
        if line.strip() and indent_level is not None:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= 8:  # Method level indentation
                break
        
        method_lines.append(line)
    
    # Create the new simple implementation
    new_method = '''def get_priority_work_batch(self, worker_id, max_tasks=5):
        """
        Get priority work for a worker using simple EDHREC rank sorting.
        Much faster than complex aggregation pipelines.
        """
        enhanced_swarm_logger.info(f"Getting work for {worker_id}, max_tasks: {max_tasks}")
        
        # Validate worker
        worker = self.workers.find_one({'worker_id': worker_id})
        if not worker:
            enhanced_swarm_logger.error(f"Worker {worker_id} not found")
            return []
        
        # Find cards that need analysis, sorted by EDHREC rank (strongest first)
        # Cards with lower edhrecRank numbers are stronger (rank 1 = strongest)
        incomplete_cards = list(self.cards.find({
            '$or': [
                {'analysis.component_count': {'$lt': 20}},
                {'analysis.component_count': {'$exists': False}}
            ]
        }).sort('edhrecRank', 1).limit(max_tasks * 2))  # Get extra for safety
        
        if not incomplete_cards:
            enhanced_swarm_logger.info("No cards need analysis")
            return []
        
        enhanced_swarm_logger.info(f"Found {len(incomplete_cards)} cards needing analysis")
        
        # Create tasks for the strongest cards
        tasks = []
        for card in incomplete_cards[:max_tasks]:
            task = self._create_simple_task(card, worker_id)
            if task:
                tasks.append(task)
        
        # Store tasks in database
        if tasks:
            self.tasks.insert_many(tasks)
            enhanced_swarm_logger.info(f"Created {len(tasks)} tasks for {worker_id}")
        
        return tasks'''
    
    # Replace the old method with the new one
    old_method_text = '\n'.join(method_lines)
    content = content.replace(old_method_text, new_method)
    
    # Add the _create_simple_task helper method
    simple_task_method = '''
    
    def _create_simple_task(self, card, worker_id):
        """Create a simple task for a single card"""
        import uuid
        from datetime import datetime, timezone
        
        # Get card identifier (handle both uuid and id fields)
        card_uuid = card.get('uuid') or card.get('id') or str(card.get('_id'))
        if not card_uuid:
            enhanced_swarm_logger.error(f"Card missing identifier: {card.get('name', 'Unknown')}")
            return None
        
        # Determine which components are needed
        existing_components = card.get('analysis', {}).get('components', {})
        existing_count = len(existing_components)
        
        # Standard components we want to generate
        all_components = [
            'summary', 'lore_analysis', 'power_analysis', 'synergy_analysis',
            'deck_inclusion', 'competitive_analysis', 'casual_analysis', 'commander_analysis',
            'flavor_analysis', 'art_analysis', 'mechanical_analysis', 'tribal_analysis',
            'combo_analysis', 'budget_analysis', 'upgrade_analysis', 'meta_analysis',
            'interaction_analysis', 'threat_assessment', 'versatility_analysis', 'fun_factor'
        ]
        
        # Find missing components
        missing_components = [comp for comp in all_components if comp not in existing_components]
        
        if not missing_components:
            enhanced_swarm_logger.info(f"Card {card.get('name')} already has all components")
            return None
        
        # Create task
        task_id = str(uuid.uuid4())
        task = {
            'task_id': task_id,
            'card_id': str(card['_id']),
            'card_uuid': card_uuid,
            'card_name': card.get('name', 'Unknown'),
            'components': missing_components[:5],  # Limit to 5 components per task
            'assigned_to': worker_id,
            'status': 'assigned',
            'created_at': datetime.now(timezone.utc),
            'assigned_at': datetime.now(timezone.utc),
            'priority_score': 1000 - (card.get('edhrecRank', 999999) or 999999),  # Higher score for lower rank
            'edhrecRank': card.get('edhrecRank'),
            'card_data': {
                'name': card.get('name'),
                'type_line': card.get('type_line'),
                'oracle_text': card.get('oracle_text', ''),
                'mana_cost': card.get('mana_cost', ''),
                'colors': card.get('colors', []),
                'rarity': card.get('rarity')
            }
        }
        
        enhanced_swarm_logger.info(f"Created task for {card.get('name')} (Rank: {card.get('edhrecRank')}, Components: {len(missing_components)})")
        return task'''
    
    # Insert the helper method before the last method or end of class
    # Find a good insertion point
    if 'def _create_simple_task(' not in content:
        # Find the end of the class or a good insertion point
        insertion_point = content.rfind('    def ')  # Find last method
        if insertion_point != -1:
            # Find the end of that method
            after_last_method = content.find('\n\nclass ', insertion_point)
            if after_last_method == -1:
                after_last_method = len(content)
            content = content[:after_last_method] + simple_task_method + content[after_last_method:]
        else:
            content += simple_task_method
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Implemented simple EDHREC-based queue system")
    print("✅ Replaced complex aggregation with direct card sorting")
    print("✅ Added _create_simple_task helper method")
    return True

if __name__ == '__main__':
    implement_simple_edhrec_queue()
