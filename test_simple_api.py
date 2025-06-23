#!/usr/bin/env python3
"""
Test the super simple API for instant work assignment
"""

import requests
import time
import json

def test_simple_api():
    """Test that the simple API is working and fast"""
    
    print("🧪 Testing SIMPLE API for instant work assignment...")
    
    API_BASE = "http://localhost:8000/api/simple_swarm"
    
    # Test 1: Register worker
    print("\n1️⃣ Registering test worker...")
    
    worker_data = {
        'worker_id': 'test_simple_worker',
        'capabilities': {
            'cpu_cores': 4,
            'ram_gb': 8,
            'gpu_available': False
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/register",
            json=worker_data,
            timeout=10
        )
        
        register_time = time.time() - start_time
        print(f"   ✅ Registration: {register_time:.2f}s - Status {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Registration failed: {response.text}")
            return
        
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Test 2: Get work (should be INSTANT)
    print("\n2️⃣ Testing INSTANT work retrieval...")
    
    work_data = {
        'worker_id': 'test_simple_worker',
        'max_tasks': 1
    }
    
    for i in range(3):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE}/get_work",
                json=work_data,
                timeout=2  # Should be instant
            )
            
            work_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                task_count = len(data.get('tasks', []))
                print(f"   ⚡ Test {i+1}: {work_time:.3f}s - Got {task_count} tasks")
                
                # Show first task if available
                if task_count > 0:
                    task = data['tasks'][0]
                    print(f"       Card: {task.get('card_name', 'Unknown')}")
                
                # If instant (< 0.1s), mark as success
                if work_time < 0.1:
                    print(f"   🎉 INSTANT! This is what we want!")
                elif work_time < 0.5:
                    print(f"   ✅ Fast enough")
                else:
                    print(f"   ⚠️  Still slow")
                    
            else:
                print(f"   ❌ Test {i+1}: {work_time:.3f}s - Status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   💔 Test {i+1}: TIMEOUT")
            
        except Exception as e:
            print(f"   ❌ Test {i+1}: Error: {e}")
        
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n✅ Simple API test completed!")

if __name__ == "__main__":
    test_simple_api()
