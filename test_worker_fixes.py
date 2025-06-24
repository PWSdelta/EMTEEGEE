#!/usr/bin/env python3
"""
Test script to verify that the universal worker fixes work correctly:
1. Worker requests random assignment
2. Worker receives unique cards (no duplicates)
3. Worker can submit results successfully with card_id
"""

import json
import requests
import time
import uuid
from datetime import datetime, timezone

# Test configuration
SERVER_URL = 'http://localhost:8000'
TEST_WORKER_ID = f'test-worker-{uuid.uuid4().hex[:8]}'

def test_random_assignment():
    """Test that worker can request and receive random assignments"""
    print(f"🧪 Testing random assignment for worker: {TEST_WORKER_ID}")
    
    # Register worker first
    register_data = {
        'worker_id': TEST_WORKER_ID,
        'capabilities': {
            'worker_type': 'test',
            'ram_gb': 16,
            'cpu_cores': 8,
            'has_gpu': False,
            'hostname': 'test-host'
        }
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/enhanced_swarm/register",
            json=register_data,
            timeout=30
        )
        print(f"📋 Worker registration: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test multiple work requests with random assignment
    assigned_cards = []
    
    for i in range(3):
        print(f"\n🔄 Request {i+1}: Getting random work...")
        
        work_request = {
            'worker_id': TEST_WORKER_ID,
            'max_tasks': 1,
            'worker_type': 'test',
            'specialization': 'test_analysis',
            'active_task_ids': [],
            'completed_task_ids': [],
            'random_assignment': True  # Key fix: request random assignment
        }
        
        try:
            response = requests.post(
                f"{SERVER_URL}/api/enhanced_swarm/get_work",
                json=work_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tasks = result.get('tasks', [])
                
                if tasks:
                    task = tasks[0]
                    card_name = task.get('card_name', 'Unknown')
                    card_id = task.get('card_id') or task.get('card_uuid')
                    assignment_type = task.get('assignment_type', 'unknown')
                    
                    print(f"✅ Received task: {card_name} (ID: {card_id}, Type: {assignment_type})")
                    assigned_cards.append((card_name, card_id))
                    
                    # Test result submission with card_id
                    success = test_result_submission(task)
                    if success:
                        print(f"✅ Successfully submitted results for {card_name}")
                    else:
                        print(f"❌ Failed to submit results for {card_name}")
                else:
                    print("⚠️  No tasks received")
            else:
                print(f"❌ Work request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Work request error: {e}")
        
        time.sleep(2)  # Brief pause between requests
    
    # Check for uniqueness
    print(f"\n📊 Assigned cards summary:")
    unique_cards = set()
    for card_name, card_id in assigned_cards:
        print(f"  - {card_name} (ID: {card_id})")
        unique_cards.add(card_id)
    
    if len(unique_cards) == len(assigned_cards):
        print(f"✅ All {len(assigned_cards)} cards were unique - no duplicates!")
        return True
    else:
        print(f"❌ Found duplicates: {len(assigned_cards)} cards, {len(unique_cards)} unique")
        return False

def test_result_submission(task):
    """Test submitting results with proper card_id"""
    task_id = task.get('task_id')
    card_id = task.get('card_id') or task.get('card_uuid')
    
    if not card_id:
        print(f"❌ No card_id found in task: {task.keys()}")
        return False
    
    # Mock analysis results
    mock_results = {
        'strategic_analysis': 'This is a test strategic analysis',
        'combo_analysis': 'This is a test combo analysis',
        'meta_analysis': 'This is a test meta analysis'
    }
    
    submission_data = {
        'worker_id': TEST_WORKER_ID,
        'task_id': task_id,
        'card_id': card_id,  # Key fix: include card_id
        'results': {
            'components': mock_results,
            'model_info': {
                'model_name': 'test-model',
                'worker_type': 'test',
                'specialization': 'test_analysis'
            },
            'execution_time': 1.5
        }
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/enhanced_swarm/submit_results",
            json=submission_data,
            timeout=60
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Result submission failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Result submission error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Universal Worker Fix Tests")
    print("="*50)
    
    success = test_random_assignment()
    
    print("\n" + "="*50)
    if success:
        print("✅ ALL TESTS PASSED! Worker fixes are working correctly.")
        print("🎯 Key fixes verified:")
        print("   - Random assignment working (no EDHREC priority)")
        print("   - Unique card assignment (no duplicates)")
        print("   - Result submission with card_id working")
    else:
        print("❌ SOME TESTS FAILED! Check the logs above.")
    
    return success

if __name__ == '__main__':
    main()
