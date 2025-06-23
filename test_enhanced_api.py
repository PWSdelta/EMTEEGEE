#!/usr/bin/env python3
"""
Test Enhanced Swarm API Worker Registration
"""

import requests
import json
from datetime import datetime, timezone

def test_enhanced_swarm_api():
    """Test the enhanced swarm API endpoints"""
    
    base_url = "http://localhost:8001/api/enhanced_swarm"
    
    print("🧪 Testing Enhanced Swarm API...")
    
    # Test 1: Status endpoint
    print("\n1. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("✅ Status endpoint working")
            status = response.json()
            print(f"   📊 {status['cards']['analyzed']}/{status['cards']['total']} cards analyzed ({status['cards']['completion_rate']})")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test 2: Worker registration
    print("\n2. Testing worker registration...")
    try:
        registration_data = {
            'worker_id': 'test-worker-123',
            'capabilities': {
                'hostname': 'test-machine',
                'worker_type': 'desktop',
                'cpu_cores': 8,
                'ram_gb': 32,
                'gpu_available': True,
                'specialization': 'fast_gpu_analysis',
                'version': '3.0.0'
            },
            'status': 'active',
            'registered_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(
            f"{base_url}/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Worker registration successful")
            result = response.json()
            print(f"   🆔 Worker ID: {result.get('worker_id', 'unknown')}")
        else:
            print(f"❌ Worker registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Worker registration error: {e}")
    
    # Test 3: Get work
    print("\n3. Testing get work endpoint...")
    try:
        work_request = {
            'worker_id': 'test-worker-123',
            'max_tasks': 1,
            'worker_type': 'desktop',
            'specialization': 'fast_gpu_analysis'
        }
        
        response = requests.post(
            f"{base_url}/get_work",
            json=work_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            tasks = result.get('tasks', [])
            print(f"✅ Get work successful - received {len(tasks)} tasks")
            if tasks:
                task = tasks[0]
                print(f"   📋 Task ID: {task.get('task_id', 'unknown')}")
                print(f"   🎴 Card: {task.get('card_data', {}).get('name', 'unknown')}")
        else:
            print(f"❌ Get work failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Get work error: {e}")
    
    print("\n🎯 Enhanced Swarm API Test Complete!")
    print("   If all tests passed, the API is ready for production deployment.")

if __name__ == "__main__":
    test_enhanced_swarm_api()
