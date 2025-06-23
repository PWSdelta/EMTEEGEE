#!/usr/bin/env python3
"""
Fix the fully_analyzed flag for cards that truly have all components
"""

import os
import sys
import django
from datetime import datetime

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_mongodb_collection
from cards.enhanced_swarm_manager import EnhancedSwarmManager

def fix_fully_analyzed_flags():
    """Fix fully_analyzed flags for cards that truly have all components"""
    
    print("=== FIXING FULLY_ANALYZED FLAGS ===")
    cards = get_mongodb_collection('cards')
    
    # Get the correct component list from the manager
    manager = EnhancedSwarmManager()
    all_required_components = set(
        manager.GPU_COMPONENTS + 
        manager.CPU_HEAVY_COMPONENTS + 
        manager.BALANCED_COMPONENTS
    )
    
    print(f"Required components ({len(all_required_components)}): {sorted(all_required_components)}")
    
    # Find cards that actually have all required components
    cards_to_check = list(cards.find({
        'analysis.components': {'$exists': True, '$ne': {}},
        'analysis.component_count': {'$gte': 15}  # At least most components
    }))
    
    print(f"Checking {len(cards_to_check)} cards...")
    
    truly_complete_cards = []
    partially_complete_cards = []
    
    for card in cards_to_check:
        card_name = card.get('name', 'Unknown')
        analysis = card.get('analysis', {})
        components = analysis.get('components', {})
        
        component_keys = set(components.keys())
        has_all_components = component_keys >= all_required_components
        
        if has_all_components:
            truly_complete_cards.append({
                'card': card,
                'name': card_name,
                'component_count': len(component_keys)
            })
        elif len(component_keys) >= 15:  # Mostly complete
            missing = all_required_components - component_keys
            partially_complete_cards.append({
                'card': card,
                'name': card_name,
                'component_count': len(component_keys),
                'missing': missing
            })
    
    print(f"\nFound {len(truly_complete_cards)} truly complete cards")
    print(f"Found {len(partially_complete_cards)} partially complete cards (15+ components)")
    
    # Fix the truly complete cards
    if truly_complete_cards:
        print(f"\n=== FIXING {len(truly_complete_cards)} COMPLETE CARDS ===")
        
        fixed_count = 0
        for item in truly_complete_cards:
            card = item['card']
            card_name = item['name']
            
            # Check if already marked
            analysis = card.get('analysis', {})
            if analysis.get('fully_analyzed') != True:
                print(f"  Fixing: {card_name} ({item['component_count']} components)")
                
                cards.update_one(
                    {'_id': card['_id']},
                    {
                        '$set': {
                            'analysis.fully_analyzed': True,
                            'analysis.analysis_completed_at': analysis.get('last_updated', datetime.now())
                        }
                    }
                )
                fixed_count += 1
            else:
                print(f"  Already marked: {card_name}")
        
        print(f"Fixed {fixed_count} cards")
    
    # Show partially complete cards
    if partially_complete_cards:
        print(f"\n=== TOP PARTIALLY COMPLETE CARDS ===")
        # Sort by component count descending
        partially_complete_cards.sort(key=lambda x: x['component_count'], reverse=True)
        
        for item in partially_complete_cards[:10]:  # Top 10
            missing_count = len(item['missing'])
            print(f"  {item['name']}: {item['component_count']}/20 components (missing {missing_count})")
            if missing_count <= 3:  # Show what's missing if close
                print(f"    Missing: {', '.join(sorted(item['missing']))}")
    
    # Verify the fix
    print(f"\n=== VERIFICATION ===")
    truly_complete_count = cards.count_documents({
        'analysis.fully_analyzed': True
    })
    
    print(f"Cards now marked as fully_analyzed: {truly_complete_count}")
    
    # Update the swarm status to see the new numbers
    from cards.enhanced_swarm_manager import enhanced_swarm
    status = enhanced_swarm.get_enhanced_swarm_status()
    
    print(f"Updated swarm status:")
    print(f"  Total cards: {status['cards']['total']:,}")
    print(f"  Analyzed cards: {status['cards']['analyzed']:,}")
    print(f"  Completion rate: {status['cards']['completion_rate']}")
    
    return {
        'truly_complete': len(truly_complete_cards),
        'partially_complete': len(partially_complete_cards),
        'fixed': fixed_count if 'fixed_count' in locals() else 0
    }

if __name__ == "__main__":
    results = fix_fully_analyzed_flags()
    print(f"\nResults: {results}")
