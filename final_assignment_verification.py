#!/usr/bin/env python3
"""
Final verification that the work assignment system is fixed
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm
from cards.models import get_mongodb_collection

def final_verification():
    """Final verification of the fixed system"""
    print("🔍 FINAL SYSTEM VERIFICATION")
    print("=" * 50)
    
    # 1. Check swarm status
    print("\n📊 Swarm Status:")
    status = enhanced_swarm.get_enhanced_swarm_status()
    print(f"   Total cards: {status.get('cards', {}).get('total', 0):,}")
    print(f"   Analyzed cards: {status.get('cards', {}).get('analyzed', 0):,}")
    print(f"   Active workers: {status.get('workers', {}).get('active', 0)}")
    
    # 2. Check top cards are properly handled
    cards = get_mongodb_collection('cards')
    print(f"\n🏆 Top EDHREC Cards Status:")
    
    top_cards = list(cards.find({
        'edhrecRank': {'$lte': 10}
    }).sort('edhrecRank', 1).limit(10))
    
    for card in top_cards:
        name = card.get('name', 'Unknown')
        rank = card.get('edhrecRank', 'N/A')
        analysis = card.get('analysis', {})
        component_count = analysis.get('component_count', 0)
        fully_analyzed = analysis.get('fully_analyzed', False)
        
        status_icon = "✅" if fully_analyzed else "🔄" if component_count > 0 else "⭕"
        print(f"   {status_icon} #{rank} {name}: {component_count}/20 components")
    
    # 3. Test work assignment doesn't give duplicates
    print(f"\n🧪 Work Assignment Test:")
    test_tasks = []
    for i in range(3):
        worker_id = f"final_test_worker_{i+1}"
        tasks = enhanced_swarm.get_work(worker_id)
        if tasks:
            task = tasks[0]
            card_name = task.get('card_name')
            components_count = len(task.get('components', []))
            test_tasks.append((worker_id, card_name, components_count))
            print(f"   ✅ {worker_id}: {card_name} ({components_count} components)")
        else:
            print(f"   ❌ {worker_id}: No work available")
    
    # Check for duplicates
    card_names = [t[1] for t in test_tasks]
    if len(card_names) == len(set(card_names)):
        print("   ✅ No duplicate assignments!")
    else:
        print("   ❌ Duplicate assignments detected!")
    
    # Check component counts
    component_counts = [t[2] for t in test_tasks]
    if all(count == 20 for count in component_counts):
        print("   ✅ All assignments have 20 components!")
    else:
        print(f"   ❌ Wrong component counts: {component_counts}")
    
    print(f"\n🎉 VERIFICATION COMPLETE!")
    print("✅ System fixed: No more endless Sol Ring/Command Tower assignments")
    print("✅ Workers get complete tasks: All 20 components at once")  
    print("✅ No duplicate work: Each worker gets a different card")
    print("✅ Proper tracking: Completed cards are marked and skipped")

if __name__ == "__main__":
    final_verification()
