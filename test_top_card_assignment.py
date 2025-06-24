#!/usr/bin/env python3
"""
Check specific assignment behavior for Sol Ring and Command Tower
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm
from cards.models import get_mongodb_collection

def check_top_card_assignments():
    """Check how the system handles Sol Ring and Command Tower"""
    print("🔍 CHECKING TOP CARD ASSIGNMENT BEHAVIOR")
    print("=" * 50)
    
    cards = get_mongodb_collection('cards')
    
    # Find Sol Ring and Command Tower
    sol_ring = cards.find_one({'name': 'Sol Ring'})
    command_tower = cards.find_one({'name': 'Command Tower'})
    
    print("\n📊 Top Card Status:")
    for card in [sol_ring, command_tower]:
        if card:
            name = card.get('name')
            edhrec_rank = card.get('edhrecRank', 'Unknown')
            analysis = card.get('analysis', {})
            component_count = analysis.get('component_count', 0)
            fully_analyzed = analysis.get('fully_analyzed', False)
            
            print(f"🎴 {name}:")
            print(f"   📈 EDHREC Rank: #{edhrec_rank}")
            print(f"   🧩 Components: {component_count}/20")
            print(f"   ✅ Fully Analyzed: {fully_analyzed}")
    
    # Check current task assignments
    tasks = get_mongodb_collection('swarm_tasks')
    
    print(f"\n📋 Current Task Assignments:")
    active_tasks = list(tasks.find({
        'status': {'$in': ['assigned', 'in_progress']},
        'card_name': {'$in': ['Sol Ring', 'Command Tower']}
    }))
    
    if active_tasks:
        print(f"⚠️  Found {len(active_tasks)} active assignments for top cards:")
        for task in active_tasks:
            card_name = task.get('card_name', 'Unknown')
            worker_id = task.get('assigned_to', 'Unknown')
            created_at = task.get('created_at')
            components = task.get('components', [])
            
            print(f"   🎯 {card_name} → {worker_id}")
            print(f"      📅 Assigned: {created_at}")
            print(f"      🧩 Components: {len(components)}")
    else:
        print("✅ No active assignments for Sol Ring or Command Tower")
    
    # Try to get work and see what happens
    print(f"\n🧪 Testing Work Assignment:")
    print("Attempting to get work for new worker...")
    
    new_tasks = enhanced_swarm.get_work('test_top_cards_worker')
    
    if new_tasks:
        task = new_tasks[0]
        card_name = task.get('card_name')
        print(f"✅ New worker got: {card_name}")
        
        if card_name in ['Sol Ring', 'Command Tower']:
            print("❌ ERROR: Top cards are still being assigned!")
        else:
            print("✅ Good: New worker got a different card")
    else:
        print("✅ No work available (all cards properly assigned)")

if __name__ == "__main__":
    check_top_card_assignments()
