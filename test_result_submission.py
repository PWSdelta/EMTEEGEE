#!/usr/bin/env python3
"""
Test the Enhanced Swarm Manager result submission fixes
"""

import os
import sys
import django
import json
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_result_submission():
    """Test the result submission pipeline"""
    print("🧪 Testing Enhanced Swarm Manager result submission...")
    
    # Register a test worker
    worker_id = "test-worker-submission"
    capabilities = {
        'gpu_available': True,
        'ram_gb': 32,
        'ollama_available': True,
        'models_available': ['qwen2.5:7b']
    }
    
    print(f"📝 Registering worker: {worker_id}")
    registration = enhanced_swarm.register_worker(worker_id, capabilities)
    print(f"✅ Registration result: {registration['status']}")
    
    # Get work for the test worker
    print(f"🔄 Getting work for worker...")
    tasks = enhanced_swarm.get_work(worker_id, max_tasks=1)
    
    if not tasks:
        print("❌ No tasks available for testing")
        return False
    
    task = tasks[0]
    task_id = task['task_id']
    card_name = task.get('card_name', 'Unknown')
    
    print(f"📋 Got task: {task_id} for card '{card_name}'")
    print(f"   Task has card_id: {task.get('card_id', 'MISSING')}")
    print(f"   Task has card_uuid: {task.get('card_uuid', 'MISSING')}")
    
    # Test result submission with mock results
    print(f"📤 Submitting mock results...")
    mock_results = {
        'components': {
            'play_tips': 'This is a test analysis component',
            'mulligan_considerations': 'Test mulligan advice'
        },
        'execution_time': 2.5,
        'model_info': {'model': 'test-model', 'version': '1.0'}
    }
    
    # Use the API-compatible method
    success = enhanced_swarm.submit_task_result(
        task_id=task_id,
        worker_id=worker_id,
        card_id=task.get('card_id') or task.get('card_uuid'),
        results=mock_results
    )
    
    if success:
        print(f"✅ Result submission successful!")
        print(f"🎯 End-to-end test PASSED - workers can now submit results")
        return True
    else:
        print(f"❌ Result submission failed")
        print(f"💥 End-to-end test FAILED")
        return False

if __name__ == "__main__":
    success = test_result_submission()
    sys.exit(0 if success else 1)
