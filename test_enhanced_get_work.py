#!/usr/bin/env python3
"""
Test the enhanced get_work endpoint to diagnose the 500 error
"""

import requests
import json

# Test the get_work endpoint directly
def test_get_work():
    url = "https://mtgabyss.com/api/enhanced_swarm/get_work"
    
    payload = {
        "worker_id": "desktop-DESKTOP-F659156",
        "max_tasks": 1,
        "specialization": "fast_gpu_analysis"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Response: {json.dumps(data, indent=2)}")
            except:
                print("Response is not valid JSON")
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("🔍 Testing enhanced get_work endpoint...")
    test_get_work()
