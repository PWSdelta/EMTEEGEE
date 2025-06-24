#!/usr/bin/env python3
"""
Debug script to see what workers are actually sending vs what server expects
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection
from cards.enhanced_swarm_manager import enhanced_swarm
import json

def debug_worker_submission():
    print("🔍 DEBUGGING WORKER SUBMISSION FORMAT")
    print("=" * 50)
    
    # Check what the enhanced_swarm_manager expects
    print("\n1. CHECKING SUBMIT_TASK_RESULT METHOD...")
    
    # Get a test card to see submission format
    cards = get_cards_collection()
    test_card = cards.find_one({'analysis.status.fully_analyzed': {'$ne': True}})
    
    if not test_card:
        print("❌ No unanalyzed cards found")
        return
    
    card_id = str(test_card['_id'])
    card_name = test_card['name']
    
    print(f"📋 Using test card: {card_name} ({card_id})")
    
    # Create test results in different formats to see which works
    test_formats = {
        'format_1_components_dict': {
            'mana_efficiency': 'This is a test analysis for mana efficiency.',
            'card_advantage': 'This is a test analysis for card advantage.',
            'synergies': 'This is a test analysis for synergies.'
        },
        'format_2_results_nested': {
            'results': {
                'mana_efficiency': 'This is a test analysis for mana efficiency.',
                'card_advantage': 'This is a test analysis for card advantage.',
                'synergies': 'This is a test analysis for synergies.'
            }
        },
        'format_3_components_list': [
            {'component': 'mana_efficiency', 'content': 'This is a test analysis for mana efficiency.'},
            {'component': 'card_advantage', 'content': 'This is a test analysis for card advantage.'},
            {'component': 'synergies', 'content': 'This is a test analysis for synergies.'}
        ]
    }
    
    print("\n2. TESTING DIFFERENT SUBMISSION FORMATS...")
    
    for format_name, test_results in test_formats.items():
        print(f"\n🧪 Testing {format_name}:")
        print(f"   Format: {json.dumps(test_results, indent=2)[:200]}...")
        
        try:
            success = enhanced_swarm.submit_task_result(
                task_id=f"test_{format_name}",
                worker_id="debug_worker",
                card_id=card_id,
                results=test_results
            )
            
            if success:
                print(f"   ✅ {format_name} WORKED!")
            else:
                print(f"   ❌ {format_name} failed")
        except Exception as e:
            print(f"   💥 {format_name} crashed: {e}")
    
    print("\n3. CHECKING ACTUAL WORKER LOGS...")
    
    # Check recent task submissions in the database
    if hasattr(enhanced_swarm, 'tasks'):
        recent_tasks = list(enhanced_swarm.tasks.find({}).sort('created_at', -1).limit(5))
        
        print(f"📊 Found {len(recent_tasks)} recent task submissions:")
        for task in recent_tasks:
            print(f"   Task: {task.get('task_id', 'unknown')}")
            print(f"   Worker: {task.get('worker_id', 'unknown')}")
            print(f"   Status: {task.get('status', 'unknown')}")
            if 'results' in task:
                print(f"   Results type: {type(task['results'])}")
                print(f"   Results keys: {list(task['results'].keys()) if isinstance(task['results'], dict) else 'not dict'}")
    
    print("\n4. CHECKING UNIVERSAL WORKER CODE...")
    
    # Check how universal_worker_enhanced.py formats results
    try:
        with open('universal_worker_enhanced.py', 'r') as f:
            content = f.read()
            
        # Look for result submission code
        if 'submit_results' in content:
            print("✅ Found submit_results in worker code")
            
            # Extract the relevant section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'submit_results' in line and 'def' not in line:
                    print(f"   Line {i+1}: {line.strip()}")
                    # Show context around this line
                    for j in range(max(0, i-3), min(len(lines), i+4)):
                        if j != i:
                            print(f"   Line {j+1}: {lines[j].strip()}")
                    break
        else:
            print("❌ No submit_results found in worker code")
            
    except FileNotFoundError:
        print("❌ universal_worker_enhanced.py not found")

if __name__ == "__main__":
    debug_worker_submission()