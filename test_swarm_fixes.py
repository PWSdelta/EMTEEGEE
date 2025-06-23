#!/usr/bin/env python3
"""
Test script to verify the result submission fixes
"""

import os
import sys
import django
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_fixes():
    """Test the enhanced swarm manager fixes"""
    print("🧪 Testing Enhanced Swarm Manager fixes...")
    
    # Test worker registration
    test_capabilities = {
        'gpu_available': True,
        'ram_gb': 32,
        'cpu_cores': 8
    }
    
    worker_id = "test-worker-001"
    registration_result = enhanced_swarm.register_worker(worker_id, test_capabilities)
    print(f"✅ Worker registration: {registration_result['status']}")
    
    # Test getting work
    work_tasks = enhanced_swarm.get_work(worker_id, max_tasks=2)
    print(f"📋 Got {len(work_tasks)} work tasks")
    
    for i, task in enumerate(work_tasks):
        print(f"  Task {i+1}: {task['card_name']} - {len(task['components'])} components")
        print(f"    Task ID: {task['task_id']}")
        print(f"    Card ID: {task['card_id']}")
        print(f"    Card UUID: {task.get('card_uuid', 'N/A')}")
    
    # Test submitting a mock result for the first task
    if work_tasks:
        test_task = work_tasks[0]
        mock_results = {
            'components': {
                'play_tips': 'This is a test play tip',
                'synergy_analysis': 'This is a test synergy analysis'
            },
            'model_info': {'model': 'test-model', 'version': '1.0'}
        }
        
        print(f"\n🧪 Testing result submission for task {test_task['task_id']}...")
        success = enhanced_swarm.submit_task_result(
            test_task['task_id'], 
            worker_id, 
            test_task['card_id'], 
            mock_results
        )
        
        print(f"📤 Result submission: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Get status
    status = enhanced_swarm.get_enhanced_swarm_status()
    print(f"\n📊 Swarm Status:")
    print(f"  Workers: {status['workers']['active']}/{status['workers']['total']} active")
    print(f"  Tasks: {status['tasks']['pending']} pending, {status['tasks']['completed']} completed")
    print(f"  Cards: {status['cards']['analyzed']}/{status['cards']['total']} ({status['cards']['completion_rate']})")

if __name__ == "__main__":
    test_fixes()
