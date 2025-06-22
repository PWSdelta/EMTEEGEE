#!/usr/bin/env python
"""
Test script for The Abyss autocomplete functionality
Tests the new autocomplete API endpoint and verifies suggestions are returned.
"""

import os
import sys
import django
from django.test import Client
import json

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def test_autocomplete_api():
    """Test the autocomplete API endpoint"""
    client = Client()
    
    print("🧪 Testing Autocomplete API...")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        'lightning',
        'bolt',
        'sol',
        'urza',
        'creature',
        'draw',
        'mh3',
        'rebecca',
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        response = client.get(f'/api/autocomplete/?q={query}')
        
        if response.status_code == 200:
            data = json.loads(response.content)
            suggestions = data.get('suggestions', [])
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Found {len(suggestions)} suggestions:")
            
            for i, suggestion in enumerate(suggestions[:5]):  # Show first 5
                text = suggestion.get('text', 'Unknown')
                category = suggestion.get('category', 'Unknown')
                suggestion_type = suggestion.get('type', 'unknown')
                
                print(f"   {i+1}. [{category}] {text} ({suggestion_type})")
            
            if len(suggestions) > 5:
                print(f"   ... and {len(suggestions) - 5} more")
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.content}")
    
    # Test edge cases
    print("\n🧪 Testing edge cases...")
    print("-" * 30)
    
    # Empty query
    response = client.get('/api/autocomplete/?q=')
    data = json.loads(response.content)
    suggestions = data.get('suggestions', [])
    print(f"Empty query: {len(suggestions)} suggestions (should be 0)")
    
    # Single character
    response = client.get('/api/autocomplete/?q=a')
    data = json.loads(response.content)
    suggestions = data.get('suggestions', [])
    print(f"Single char 'a': {len(suggestions)} suggestions (should be 0)")
    
    # Two characters
    response = client.get('/api/autocomplete/?q=li')
    data = json.loads(response.content)
    suggestions = data.get('suggestions', [])
    print(f"Two chars 'li': {len(suggestions)} suggestions")
    
    print("\n✨ Autocomplete API tests completed!")

if __name__ == '__main__':
    test_autocomplete_api()
