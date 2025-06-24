#!/usr/bin/env python3
"""
Test real worker integration to ensure submit_results works correctly
"""

import os
import sys
import django
import requests
import json

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def test_worker_api_integration():
    """Test the actual API endpoints that workers use"""
    
    print("🧪 TESTING REAL WORKER API INTEGRATION")
    print("=" * 50)
    
    # Test 1: Register worker via enhanced swarm manager
    worker_id = "integration_test_worker"
    print(f"👷 Registering worker: {worker_id}")
    
    enhanced_swarm.register_worker(worker_id, {
        'type': 'gpu',
        'model': 'test',
        'capabilities': ['all_components']
    })
    
    # Test 2: Get work via enhanced swarm manager
    print(f"\n📋 Getting work for worker: {worker_id}")
    tasks = enhanced_swarm.get_work(worker_id)
    
    if not tasks:
        print("❌ No work available")
        return False
    
    task = tasks[0]
    print(f"✅ Got task: {task['task_id']}")
    print(f"   Card: {task['card_name']}")
    print(f"   Components: {len(task['components'])}")
    
    # Test 3: Submit results via enhanced swarm manager
    print(f"\n📤 Submitting results for task: {task['task_id']}")
    
    # Create results in the format that workers actually send
    mock_results = {
        'results': {}
    }
    
    # Add content for each component
    for component in task['components']:
        mock_results['results'][component] = f"Test analysis content for {component} of {task['card_name']}"
    
    print(f"   Submitting {len(mock_results['results'])} component results")
    
    # Submit via enhanced swarm manager (not API)
    success = enhanced_swarm.submit_task_result(
        task_id=task['task_id'],
        worker_id=worker_id,
        card_id=task['card_id'],
        results=mock_results
    )
    
    if success:
        print("✅ Results submitted successfully via swarm manager")
        
        # Verify card completion
        cards = enhanced_swarm.cards
        card = cards.find_one({'_id': enhanced_swarm.cards.find_one({'uuid': task['card_uuid']})['_id']})
        
        if card:
            analysis = card.get('analysis', {})
            is_fully_analyzed = analysis.get('fully_analyzed', False)
            component_count = analysis.get('component_count', 0)
            
            print(f"✅ Card verification:")
            print(f"   Fully analyzed: {is_fully_analyzed}")
            print(f"   Component count: {component_count}")
            
            if is_fully_analyzed and component_count == 20:
                print("🎉 SUCCESS: Card properly marked as complete!")
                return True
            else:
                print("❌ FAILURE: Card not properly marked as complete")
                return False
        else:
            print("❌ Could not find card for verification")
            return False
    else:
        print("❌ Results submission failed")
        return False

def test_api_endpoints():
    """Test the actual HTTP API endpoints"""
    
    print("\n🧪 TESTING HTTP API ENDPOINTS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    worker_id = "api_test_worker"
    
    try:
        # Test register_worker endpoint
        print("👷 Testing worker registration endpoint...")
        register_data = {
            'worker_id': worker_id,
            'capabilities': {'type': 'gpu', 'model': 'test'}
        }
        
        response = requests.post(
            f"{base_url}/api/enhanced_swarm/register_worker",
            json=register_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Worker registration endpoint works")
        else:
            print(f"❌ Worker registration failed: {response.status_code} - {response.text}")
            return False
        
        # Test get_work endpoint
        print("📋 Testing get work endpoint...")
        work_data = {'worker_id': worker_id}
        
        response = requests.post(
            f"{base_url}/api/enhanced_swarm/get_work",
            json=work_data,
            timeout=10
        )
        
        if response.status_code == 200:
            work_response = response.json()
            tasks = work_response.get('tasks', [])
            
            if tasks:
                task = tasks[0]
                print(f"✅ Get work endpoint works - got task: {task.get('task_id', 'unknown')}")
                
                # Test submit_results endpoint
                print("📤 Testing submit results endpoint...")
                
                results_data = {
                    'worker_id': worker_id,
                    'task_id': task['task_id'],
                    'card_id': task['card_id'],
                    'results': {
                        'results': {
                            component: f"API test content for {component}"
                            for component in task['components']
                        }
                    }
                }
                
                response = requests.post(
                    f"{base_url}/api/enhanced_swarm/submit_results",
                    json=results_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print("✅ Submit results endpoint works")
                    return True
                else:
                    print(f"❌ Submit results failed: {response.status_code} - {response.text}")
                    return False
            else:
                print("❌ No tasks returned from get_work endpoint")
                return False
        else:
            print(f"❌ Get work failed: {response.status_code} - {response.text}")
            return False
    
    except requests.RequestException as e:
        print(f"❌ API test failed due to connection error: {e}")
        print("   Note: Make sure Django server is running on localhost:8000")
        return False

if __name__ == "__main__":
    print("🚀 WORKER INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Direct swarm manager integration
    swarm_test_passed = test_worker_api_integration()
    
    # Test 2: HTTP API endpoints (only if server is running)
    api_test_passed = test_api_endpoints()
    
    # Results
    print("\n" + "=" * 60)
    print("🏁 INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"Swarm Manager Test: {'✅ PASSED' if swarm_test_passed else '❌ FAILED'}")
    print(f"HTTP API Test: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    
    if swarm_test_passed and api_test_passed:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("🔥 Worker integration is working correctly!")
    elif swarm_test_passed:
        print("\n✅ Core functionality works - HTTP API may need server running")
    else:
        print("\n⚠️  CORE TESTS FAILED - Please check the implementation.")
