#!/usr/bin/env python3
"""
Quick fix for the corrupted worker file
"""

# Read the current file and fix the formatting issues
with open('universal_worker_enhanced.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific formatting issues
content = content.replace('self._process_task(task)                else:', 'self._process_task(task)\n                else:')
content = content.replace('logger.debug("ℹ️  No tasks available")            else:', 'logger.debug("ℹ️  No tasks available")\n            else:')

# Make sure the card_id fix is in the _process_task method
if "'card_id': card_id," not in content:
    # Find the results dictionary and add card_id
    old_results = """results = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'status': 'completed',
                'results': {'placeholder': 'analysis_data'},
                'completed_at': datetime.now(timezone.utc).isoformat()
            }"""
    
    new_results = """results = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'card_id': card_id,  # Required by API
                'status': 'completed',
                'results': {'placeholder': 'analysis_data'},
                'completed_at': datetime.now(timezone.utc).isoformat()
            }"""
    
    content = content.replace(old_results, new_results)

# Make sure we extract card_id from task
if "card_id = task.get('card_id') or task.get('card_uuid')" not in content:
    # Find the task processing and add card_id extraction
    old_task_processing = """task_id = task.get('task_id', 'unknown')
        card_name = task.get('card_name', 'Unknown Card')"""
    
    new_task_processing = """task_id = task.get('task_id', 'unknown')
        card_name = task.get('card_name', 'Unknown Card')
        card_id = task.get('card_id') or task.get('card_uuid')  # Support both field names"""
    
    content = content.replace(old_task_processing, new_task_processing)

# Write the fixed content
with open('universal_worker_enhanced.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed universal_worker_enhanced.py formatting and added card_id field")
