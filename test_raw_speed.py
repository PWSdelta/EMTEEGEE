#!/usr/bin/env python3
"""
Super simple test - just hit get_work endpoint
"""

import requests
import time

def test_raw_speed():
    """Test just the get_work endpoint speed"""
    url = "http://localhost:8000/api/simple_swarm/get_work"
    
    for i in range(3):
        start_time = time.time()
        
        try:
            response = requests.post(url, json={'worker_id': 'speed_test'}, timeout=10)
            elapsed = time.time() - start_time
            
            print(f"Test {i+1}: {elapsed:.3f}s - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get('tasks', [])
                if tasks:
                    print(f"         Got card: {tasks[0].get('card_name', 'Unknown')}")
                else:
                    print(f"         No tasks returned")
            else:
                print(f"         Error: {response.text}")
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"Test {i+1}: {elapsed:.3f}s - Error: {e}")
        
        time.sleep(0.1)  # Brief pause

if __name__ == "__main__":
    test_raw_speed()
