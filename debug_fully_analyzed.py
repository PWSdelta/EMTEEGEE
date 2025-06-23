#!/usr/bin/env python3
"""
Debug why fully_analyzed is not being set correctly
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_mongodb_collection

def debug_fully_analyzed():
    """Debug why fully_analyzed flag is not being set"""
    
    print("=== DEBUGGING FULLY_ANALYZED FLAG ===")
    cards = get_mongodb_collection('cards')
    
    # Get expected components from enhanced_swarm_manager
    all_expected_components = [
        'play_tips', 'mulligan_considerations', 'rules_clarifications',
        'combo_suggestions', 'format_analysis', 'synergy_analysis',
        'competitive_analysis', 'tactical_analysis', 'thematic_analysis',
        'historical_context', 'art_flavor_analysis', 'design_philosophy',
        'advanced_interactions', 'meta_positioning', 'budget_alternatives',
        'deck_archetypes', 'new_player_guide', 'sideboard_guide',
        'power_level_assessment', 'investment_outlook'
    ]
    
    print(f"Expected components: {len(all_expected_components)}")
    print(f"Components: {all_expected_components}")
    
    # Find cards with all 20 components
    cards_with_all_components = list(cards.find({
        '$and': [
            {f'analysis.components.{comp}': {'$exists': True}}
            for comp in all_expected_components
        ]
    }).limit(5))
    
    print(f"\nCards with all {len(all_expected_components)} components: {len(cards_with_all_components)}")
    
    # Check first few cards
    for i, card in enumerate(cards_with_all_components[:3], 1):
        print(f"\nCard {i}: {card.get('name', 'Unknown')}")
        analysis = card.get('analysis', {})
        
        print(f"  analysis.fully_analyzed: {analysis.get('fully_analyzed', 'NOT SET')}")
        print(f"  analysis.component_count: {analysis.get('component_count', 'NOT SET')}")
        
        components = analysis.get('components', {})
        component_keys = set(components.keys())
        expected_set = set(all_expected_components)
        
        print(f"  Component keys found: {len(component_keys)}")
        print(f"  Expected components: {len(expected_set)}")
        print(f"  Has all components: {component_keys >= expected_set}")
        
        missing = expected_set - component_keys
        extra = component_keys - expected_set
        
        if missing:
            print(f"  Missing components: {missing}")
        if extra:
            print(f"  Extra components: {extra}")
    
    # Test the logic from enhanced_swarm_manager
    print(f"\n=== TESTING LOGIC ===")
    
    # This mimics the logic in submit_enhanced_results
    from cards.enhanced_swarm_manager import EnhancedSwarmManager
    manager = EnhancedSwarmManager()
    
    all_components_from_manager = set(
        manager.GPU_COMPONENTS + 
        manager.CPU_HEAVY_COMPONENTS + 
        manager.BALANCED_COMPONENTS
    )
    
    print(f"Components from manager: {len(all_components_from_manager)}")
    print(f"Manager components: {sorted(all_components_from_manager)}")
    
    # Check if they match our expected list
    expected_set = set(all_expected_components)
    print(f"Sets match: {all_components_from_manager == expected_set}")
    
    if all_components_from_manager != expected_set:
        print(f"Difference: {all_components_from_manager.symmetric_difference(expected_set)}")
    
    # Manually fix some cards to test
    print(f"\n=== MANUAL FIX TEST ===")
    
    cards_to_fix = list(cards.find({
        'analysis.component_count': 20,
        'analysis.fully_analyzed': {'$ne': True}
    }).limit(3))
    
    print(f"Found {len(cards_to_fix)} cards with 20 components but not marked fully_analyzed")
    
    for card in cards_to_fix:
        card_id = card['_id']
        card_name = card.get('name', 'Unknown')
        
        analysis = card.get('analysis', {})
        components = analysis.get('components', {})
        component_keys = set(components.keys())
        
        if component_keys >= all_components_from_manager:
            print(f"  Fixing card: {card_name}")
            cards.update_one(
                {'_id': card_id},
                {
                    '$set': {
                        'analysis.fully_analyzed': True,
                        'analysis.analysis_completed_at': analysis.get('last_updated')
                    }
                }
            )
        else:
            missing = all_components_from_manager - component_keys
            print(f"  Card {card_name} missing: {missing}")

if __name__ == "__main__":
    debug_fully_analyzed()
