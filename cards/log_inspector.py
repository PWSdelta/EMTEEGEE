#!/usr/bin/env python3
"""
Inspect worker logs to see what's actually being submitted
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm
import json
from datetime import datetime, timedelta

def inspect_recent_submissions():
    print("🔍 INSPECTING RECENT WORKER SUBMISSIONS")
    print("=" * 50)
    
    # Look at recent tasks
    if hasattr(enhanced_swarm, 'tasks'):
        recent_tasks = list(enhanced_swarm.tasks.find({}).sort('created_at', -1).limit(10))
        
        print(f"📊 Found {len(recent_tasks)} recent tasks:")
        
        for i, task in enumerate(recent_tasks, 1):
            print(f"\n{i}. Task ID: {task.get('task_id', 'unknown')}")
            print(f"   Worker: {task.get('worker_id', 'unknown')}")
            print(f"   Card ID: {task.get('card_id', 'unknown')}")
            print(f"   Status: {task.get('status', 'unknown')}")
            print(f"   Created: {task.get('created_at', 'unknown')}")
            
            if 'results' in task:
                results = task['results']
                print(f"   Results type: {type(results)}")
                
                if isinstance(results, dict):
                    print(f"   Results keys: {list(results.keys())}")
                    
                    # Check if it contains analysis content
                    has_content = False
                    for key, value in results.items():
                        if isinstance(value, str) and len(value) > 50:
                            has_content = True
                            print(f"   ✅ Found content in '{key}': {value[:100]}...")
                        elif isinstance(value, dict):
                            print(f"   📁 Nested dict in '{key}': {list(value.keys())}")
                        else:
                            print(f"   📄 '{key}': {str(value)[:50]}...")
                    
                    if not has_content:
                        print("   ⚠️  NO MEANINGFUL CONTENT FOUND")
                else:
                    print(f"   Results content: {str(results)[:200]}...")
            else:
                print("   ❌ No results field found")
    
    # Also check what cards have been marked as analyzed
    print("\n" + "=" * 50)
    print("📊 CHECKING RECENTLY ANALYZED CARDS")
    
    cards = enhanced_swarm.cards
    recent_analyzed = list(cards.find({
        'analysis.status.fully_analyzed': True
    }).sort('analysis.status.last_updated', -1).limit(5))
    
    print(f"Found {len(recent_analyzed)} recently analyzed cards:")
    
    for card in recent_analyzed:
        print(f"\n📋 {card['name']}")
        print(f"   Card ID: {card['_id']}")
        analysis = card.get('analysis', {})
        components = analysis.get('components', {})
        print(f"   Components: {len(components)} components")
        
        if components:
            for comp_name, comp_data in list(components.items())[:3]:  # Show first 3
                if isinstance(comp_data, dict):
                    content = comp_data.get('content', comp_data.get('analysis_content', ''))
                    print(f"   - {comp_name}: {content[:100]}...")
                else:
                    print(f"   - {comp_name}: {str(comp_data)[:100]}...")

if __name__ == "__main__":
    inspect_recent_submissions()