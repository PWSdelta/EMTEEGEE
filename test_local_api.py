#!/usr/bin/env python3
"""
Quick test script to verify local API endpoints are working
"""
import requests
import json

def test_endpoint(url, description):
    try:
        print(f"\n=== Testing {description} ===")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:            try:
                data = response.json()
                print(f"JSON Response: {json.dumps(data, indent=2)}")
            except ValueError:
                print(f"Text Response: {response.text[:200]}...")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    base_url = "http://localhost:8001"
    
    # Test main page
    test_endpoint(f"{base_url}/", "Main Page")
    
    # Test swarm API endpoints
    test_endpoint(f"{base_url}/api/swarm/status/", "Swarm Status")
    test_endpoint(f"{base_url}/api/swarm/register/", "Swarm Register")
    test_endpoint(f"{base_url}/api/swarm/get_work/", "Get Work")

if __name__ == "__main__":
    main()
