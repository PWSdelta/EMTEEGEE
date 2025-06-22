#!/usr/bin/env python
"""
Simple test for the autocomplete API endpoint
"""

import os
import sys
import django
from django.test import Client

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def test_autocomplete_simple():
    """Simple test of autocomplete API"""
    client = Client()
    
    print("🧪 Testing Autocomplete API...")
    
    # Test a simple query
    query = 'lightning'
    response = client.get(f'/api/autocomplete/?q={query}')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.get('Content-Type', 'Not set')}")
    print(f"Response Content: {response.content[:200]}...")  # First 200 chars
    
    if response.status_code != 200:
        print(f"Error response: {response.content.decode()}")
    
    # Test the URL pattern is working
    response = client.get('/api/autocomplete/')
    print(f"\nEmpty query status: {response.status_code}")
    print(f"Empty query content: {response.content[:200]}...")

if __name__ == '__main__':
    test_autocomplete_simple()
