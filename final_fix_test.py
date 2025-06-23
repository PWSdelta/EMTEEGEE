#!/usr/bin/env python3
"""
Final patch script to fix result submission and test the swarm
"""

import os
import sys
import django
from pymongo import MongoClient

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def test_result_submission_directly():
    """Test result submission with the API directly"""
    print("🧪 Testing result submission with API...")
    
    # Connect to MongoDB directly
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emteegee_dev']
    
    # Get a recent task
    recent_task = db.swarm_tasks.find_one({'status': 'assigned'})
    if not recent_task:
        print("❌ No assigned tasks found")
        return
    
    print(f"📋 Found task: {recent_task['task_id']} for {recent_task['card_name']}")
    
    # Try to find the card for this task
    card_id = recent_task['card_id']
    card_name = recent_task['card_name']
    
    # Method 1: By MongoDB _id (ObjectId)
    try:
        from bson import ObjectId
        card = db.cards.find_one({'_id': ObjectId(card_id)})
        print(f"🔍 Card lookup by ObjectId: {'✅ Found' if card else '❌ Not found'}")
    except:
        card = None
        print(f"🔍 Card lookup by ObjectId: ❌ Failed")
    
    # Method 2: By UUID
    if not card:
        card = db.cards.find_one({'uuid': card_id})
        print(f"🔍 Card lookup by UUID: {'✅ Found' if card else '❌ Not found'}")
    
    # Method 3: By ID
    if not card:
        card = db.cards.find_one({'id': card_id})
        print(f"🔍 Card lookup by ID: {'✅ Found' if card else '❌ Not found'}")
    
    # Method 4: By name (last resort)
    if not card:
        card = db.cards.find_one({'name': card_name})
        print(f"🔍 Card lookup by name: {'✅ Found' if card else '❌ Not found'}")
        if card:
            print(f"   Card UUID: {card.get('uuid')}")
            print(f"   Card ID: {card.get('id')}")
    
    if card:
        print("✅ Card found! Result submission should work.")
        
        # Test the submission using the API endpoint
        import requests
        
        test_result = {
            "components": {
                "play_tips": "Test play tip for debugging",
                "synergy_analysis": "Test synergy analysis for debugging"
            },
            "model_info": {"model": "debug-test", "version": "1.0"},
            "execution_time": 2.5
        }
        
        # Make API call
        try:
            response = requests.post(
                'http://localhost:8000/cards/enhanced-swarm/submit-result/',
                json={
                    'task_id': recent_task['task_id'],
                    'worker_id': recent_task['assigned_to'],
                    'card_id': card_id,
                    'results': test_result
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📤 API Result submission: ✅ SUCCESS")
                print(f"   Response: {result}")
            else:
                print(f"📤 API Result submission: ❌ FAILED (HTTP {response.status_code})")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"📤 API Result submission: ❌ FAILED - {str(e)}")
    
    else:
        print("❌ Card not found - this is the root cause of result submission failures")

if __name__ == "__main__":
    test_result_submission_directly()
