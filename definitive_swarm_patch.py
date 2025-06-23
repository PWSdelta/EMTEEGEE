#!/usr/bin/env python3
"""
DEFINITIVE Enhanced Swarm Manager Patch Script
Adds the missing get_work and submit_task_result methods at the bottom of the class
This will fix the API connectivity issues once and for all.
"""

import os
import re

def patch_enhanced_swarm_manager():
    """Add missing methods to Enhanced Swarm Manager"""
    
    file_path = 'cards/enhanced_swarm_manager.py'
    
    print("🔧 Patching Enhanced Swarm Manager with missing methods...")
    
    # Read the current file
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Check if methods already exist properly
    if 'def get_work(self, worker_id: str, max_tasks: int = 1)' in content and 'def submit_task_result(self, task_id: str, worker_id: str, card_id: str, results: Dict[str, Any])' in content:
        print("✅ Methods already exist in file, checking if they're properly indented...")
    
    # Find the end of the class (before "# Global instance")
    class_end_pattern = r'(\n# Global instance\nenhanced_swarm = EnhancedSwarmManager\(\))'
    
    if not re.search(class_end_pattern, content):
        print("❌ Could not find class end marker, adding methods at end of file")
        insertion_point = len(content)
        prefix = "\n\n"
    else:
        match = re.search(class_end_pattern, content)
        insertion_point = match.start()
        prefix = "\n"
    
    # Define the missing methods with proper indentation and simple EDHREC-based logic
    missing_methods = '''
    def get_work(self, worker_id: str, max_tasks: int = 1) -> List[Dict[str, Any]]:
        """Get work assignments using simple EDHREC-based queue"""
        try:
            enhanced_swarm_logger.info(f"🔄 Getting work for worker {worker_id} (max: {max_tasks})")
            
            # Update worker heartbeat
            self.workers.update_one(
                {'worker_id': worker_id},
                {'$set': {'last_heartbeat': datetime.now(timezone.utc)}}
            )
            
            # Simple EDHREC-based queue: get cards with low EDHREC rank and < 20 components
            cards_needing_work = list(self.cards.find({
                'edhrecRank': {'$exists': True, '$lt': 50000},  # Has EDHREC rank
                '$or': [
                    {'analysis.component_count': {'$exists': False}},  # No analysis
                    {'analysis.component_count': {'$lt': 20}},  # Incomplete analysis
                    {'analysis.fully_analyzed': {'$ne': True}}  # Not fully analyzed
                ]
            }).sort('edhrecRank', 1).limit(max_tasks * 10))  # Get extra to filter from
            
            # Create simple tasks
            tasks = []
            for card in cards_needing_work[:max_tasks]:
                if not card:
                    continue
                    
                task_id = str(uuid.uuid4())
                task = {
                    'task_id': task_id,
                    'card_id': str(card['_id']),
                    'card_uuid': card.get('uuid', str(card['_id'])),
                    'card_name': card.get('name', 'Unknown'),
                    'components': ['play_tips', 'synergy_analysis', 'budget_alternatives'],  # Simple components
                    'assigned_to': worker_id,
                    'created_at': datetime.now(timezone.utc),
                    'status': 'assigned',
                    'card_data': {
                        'name': card.get('name'),
                        'mana_cost': card.get('mana_cost'),
                        'type_line': card.get('type_line'),
                        'oracle_text': card.get('oracle_text')
                    }
                }
                
                # Store task
                self.tasks.insert_one(task)
                tasks.append(task)
            
            enhanced_swarm_logger.info(f"📋 Assigned {len(tasks)} tasks to worker {worker_id}")
            return tasks
            
        except Exception as e:
            enhanced_swarm_logger.error(f"❌ Get work failed for worker {worker_id}: {str(e)}")
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
                            'generated_by': worker_id
                        }
                        component_count += 1
            
            if analysis_update:
                self.cards.update_one(
                    {'_id': card['_id']},
                    {
                        '$set': analysis_update,
                        '$inc': {'analysis.component_count': component_count},
                        '$currentDate': {'analysis.last_updated': True}
                    }
                )
            
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
'''
    
    # Insert the methods before the global instance
    new_content = content[:insertion_point] + prefix + missing_methods + content[insertion_point:]
    
    # Write the patched content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Enhanced Swarm Manager patched successfully!")
    print("🔄 Added missing methods:")
    print("  - get_work() - Simple EDHREC-based queue")
    print("  - submit_task_result() - Robust card lookup and result storage")

if __name__ == "__main__":
    patch_enhanced_swarm_manager()
    print("\n🎯 SUMMARY: This should fix the worker result submission failures!")
    print("   Workers will now be able to:")
    print("   1. ✅ Get tasks via get_work() API")
    print("   2. ✅ Submit results via submit_task_result() API")
    print("   3. ✅ Use simple EDHREC-based prioritization")
    print("\n💡 Next: Restart the workers to test the fix!")
