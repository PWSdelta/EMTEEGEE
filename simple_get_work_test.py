#!/usr/bin/env python3
"""
Simple test for enhanced swarm get_work method
"""
import requests
import json

def test_get_work():
    try:
        # Test get_work endpoint
        work_request = {
            'worker_id': 'test-worker-simple',
            'max_tasks': 1,
            'worker_type': 'desktop'
        }
        
        response = requests.post(
            "http://localhost:8001/api/enhanced_swarm/get_work",
            json=work_request,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ get_work method is working!")
            return True
        else:
            print("❌ get_work method failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing get_work: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing get_work method...")
    test_get_work()
