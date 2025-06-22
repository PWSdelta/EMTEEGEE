#!/usr/bin/env python3
import requests

try:
    response = requests.get('http://64.23.130.187:8000/')
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
    print(f"Content Length: {len(response.text)}")
    print("\nFirst 500 characters of response:")
    print(response.text[:500])
    print("\n" + "="*50)
    
    # Check if it contains the old status page content
    if "Status Page" in response.text or "System Status" in response.text:
        print("❌ Still showing status page content")
    elif "Welcome to EmTeeGee" in response.text or "Magic: The Gathering" in response.text:
        print("✅ Showing proper home page content")
    else:
        print("⚠️  Unknown content type")
        
except Exception as e:
    print(f"Error: {e}")
