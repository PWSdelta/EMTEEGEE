#!/usr/bin/env python3
"""Debug result submission issues"""

import os
import sys
import django
import json
from bson import ObjectId

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_mongodb_collection

def debug_result_submission():
    """Debug why result submission is failing"""
    print("🔍 Debugging result submission failures...")
    
    # Get collections
    cards = get_mongodb_collection('cards')
    tasks = get_mongodb_collection('swarm_tasks')
    
    # Find recent failed tasks
    print("\n📋 Recent tasks:")
    recent_tasks = list(tasks.find({}).sort([('created_at', -1)]).limit(5))
    for task in recent_tasks:
        print(f"  Task: {task['task_id']}")
        print(f"  Card: {task['card_name']} (UUID: {task['card_uuid']})")
        print(f"  Status: {task['status']}")
        print(f"  Card ID: {task['card_id']}")
        print()
    
    # Check if the cards exist in database
    print("\n🔍 Checking card existence:")
    for task in recent_tasks[:2]:  # Check first 2
        card_uuid = task['card_uuid']
        card_id = task['card_id']
        
        print(f"\nChecking card: {task['card_name']}")
        print(f"  UUID: {card_uuid}")
        print(f"  Card ID: {card_id}")
        
        # Try to find by UUID
        card_by_uuid = cards.find_one({'uuid': card_uuid})
        print(f"  Found by UUID: {'YES' if card_by_uuid else 'NO'}")
        
        # Try to find by _id
        try:
            card_by_id = cards.find_one({'_id': ObjectId(card_id)})
            print(f"  Found by _id: {'YES' if card_by_id else 'NO'}")
        except Exception as e:
            print(f"  Error finding by _id: {e}")
        
        # Try to find by id field
        card_by_id_field = cards.find_one({'id': card_id})
        print(f"  Found by id field: {'YES' if card_by_id_field else 'NO'}")
        
        # Try to find by name
        card_by_name = cards.find_one({'name': task['card_name']})
        print(f"  Found by name: {'YES' if card_by_name else 'NO'}")
        
        # If found by name, show its structure
        if card_by_name:
            print(f"  Card structure:")
            print(f"    _id: {card_by_name.get('_id')}")
            print(f"    uuid: {card_by_name.get('uuid')}")
            print(f"    id: {card_by_name.get('id')}")
            print(f"    name: {card_by_name.get('name')}")
            
            # Check if UUID matches
            if card_by_name.get('uuid') != card_uuid:
                print(f"    ⚠️  UUID MISMATCH! Task UUID: {card_uuid}, Card UUID: {card_by_name.get('uuid')}")
    
    # Sample a few cards to see their structure
    print("\n📊 Sample card structures:")
    sample_cards = list(cards.find({}).limit(3))
    for i, card in enumerate(sample_cards):
        print(f"\nCard {i+1}: {card.get('name', 'Unknown')}")
        print(f"  _id: {card.get('_id')}")
        print(f"  uuid: {card.get('uuid')}")
        print(f"  id: {card.get('id')}")
        print(f"  Has analysis: {'analysis' in card}")
        if 'analysis' in card:
            print(f"  Components: {list(card['analysis'].get('components', {}).keys())}")

if __name__ == "__main__":
    debug_result_submission()
