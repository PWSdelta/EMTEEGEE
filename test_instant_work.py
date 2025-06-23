#!/usr/bin/env python3
"""
Test script to verify enhanced API get_work is now instant
"""

import requests
import time
import json

API_BASE = "http://localhost:8000/api/simple_swarm"

def test_instant_work():
    """Test that get_work responds instantly with priority cache"""
    
    print("🧪 Testing Enhanced API instant work assignment...")
    
    # Test 1: Register worker
    worker_data = {
        'worker_id': 'test_instant_worker',
        'capabilities': {
            'cpu_cores': 4,
            'ram_gb': 8,
            'gpu_available': False,
            'preferred_components': ['pricing', 'legality', 'gameplay']
        }
    }
    
    print("\n1️⃣ Registering test worker...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/register",
            json=worker_data,
            timeout=10
        )
        
        register_time = time.time() - start_time
        print(f"   ✅ Registration: {register_time:.2f}s - {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Registration failed: {response.text}")
            return
        
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Test 2: Get work (should be instant with priority cache)
    work_data = {
        'worker_id': 'test_instant_worker',
        'max_tasks': 3
    }
    
    print("\n2️⃣ Testing instant work retrieval...")
    
    for i in range(3):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE}/get_work",
                json=work_data,
                timeout=5  # Should be instant, so 5s timeout
            )
            
            work_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                task_count = len(data.get('tasks', []))
                print(f"   ⚡ Test {i+1}: {work_time:.3f}s - Got {task_count} tasks")
                
                # If instant (< 0.5s), mark as success
                if work_time < 0.5:
                    print(f"   🎉 INSTANT RESPONSE! Priority cache is working!")
                else:
                    print(f"   ⚠️  Still slow - priority cache may not be active")
                    
            else:
                print(f"   ❌ Test {i+1}: {work_time:.3f}s - Status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            timeout_time = time.time() - start_time
            print(f"   💔 Test {i+1}: TIMEOUT after {timeout_time:.1f}s")
            
        except Exception as e:
            error_time = time.time() - start_time
            print(f"   ❌ Test {i+1}: {error_time:.3f}s - Error: {e}")
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n✅ Instant work test completed!")
    print("\n💡 Expected results after priority cache fix:")
    print("   - All get_work calls should be < 0.5 seconds")
    print("   - No SSL timeouts or connection issues")
    print("   - Tasks returned with proper priority scoring")

if __name__ == "__main__":
    test_instant_work()
