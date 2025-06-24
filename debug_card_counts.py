#!/usr/bin/env python3
"""
Debug script to analyze card counting logic and identify discrepancies
"""

import os
import sys
import django
from datetime import datetime

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_mongodb_collection

def analyze_card_counts():
    """Analyze different card counting methods to identify the issue"""
    
    print("=== CARD COUNT ANALYSIS ===")
    cards = get_mongodb_collection('cards')
    
    # 1. Total cards
    total_cards = cards.count_documents({})
    print(f"Total cards: {total_cards}")
    
    # 2. Current enhanced swarm logic
    current_logic_count = cards.count_documents({
        '$or': [
            {'analysis.fully_analyzed': True},
            {'analysis.analysis_completed_at': {'$exists': True, '$ne': None}}
        ]
    })
    print(f"Current logic count: {current_logic_count}")
    
    # 3. Break down by individual criteria
    fully_analyzed_count = cards.count_documents({'analysis.fully_analyzed': True})
    print(f"analysis.fully_analyzed = True: {fully_analyzed_count}")
    
    analysis_completed_at_count = cards.count_documents({
        'analysis.analysis_completed_at': {'$exists': True, '$ne': None}
    })
    print(f"analysis.analysis_completed_at exists: {analysis_completed_at_count}")
    
    # 4. Legacy fields that might be used
    legacy_fully_analyzed = cards.count_documents({'fully_analyzed': True})
    print(f"Legacy fully_analyzed = True: {legacy_fully_analyzed}")
    
    analysis_completed_at_legacy = cards.count_documents({
        'analysis_completed_at': {'$exists': True, '$ne': None}
    })
    print(f"Legacy analysis_completed_at exists: {analysis_completed_at_legacy}")
    
    # 5. Cards with any analysis components
    cards_with_components = cards.count_documents({
        'analysis.components': {'$exists': True, '$ne': {}}
    })
    print(f"Cards with analysis.components: {cards_with_components}")
    
    # 6. Cards with component_count > 0
    cards_with_component_count = cards.count_documents({
        'analysis.component_count': {'$gt': 0}
    })
    print(f"Cards with analysis.component_count > 0: {cards_with_component_count}")
    
    # 7. Sample analyzed cards to understand structure
    print("\n=== SAMPLE ANALYZED CARDS ===")
    sample_cards = list(cards.find({
        'analysis.components': {'$exists': True, '$ne': {}}
    }).limit(3))
    
    for i, card in enumerate(sample_cards, 1):
        print(f"\nSample Card {i}: {card.get('name', 'Unknown')}")
        analysis = card.get('analysis', {})
        
        print(f"  fully_analyzed: {analysis.get('fully_analyzed', 'Not set')}")
        print(f"  analysis_completed_at: {analysis.get('analysis_completed_at', 'Not set')}")
        print(f"  component_count: {analysis.get('component_count', 'Not set')}")
        
        components = analysis.get('components', {})
        print(f"  components: {len(components)} found")
        print(f"  component keys: {list(components.keys())[:5]}...")  # First 5 keys
        
        # Check legacy fields
        print(f"  legacy fully_analyzed: {card.get('fully_analyzed', 'Not set')}")
        print(f"  legacy analysis_completed_at: {card.get('analysis_completed_at', 'Not set')}")
    
    # 8. Cards with all expected components (20 total)
    all_expected_components = [
        'play_tips', 'mulligan_considerations', 'rules_clarifications',
        'combo_suggestions', 'format_analysis', 'synergy_analysis',
        'competitive_analysis', 'tactical_analysis', 'thematic_analysis',
        'historical_context', 'art_flavor_analysis', 'design_philosophy',
        'advanced_interactions', 'meta_positioning', 'budget_alternatives',
        'deck_archetypes', 'new_player_guide', 'sideboard_guide',
        'power_level_assessment', 'investment_outlook'
    ]
    
    cards_with_all_components = cards.count_documents({
        '$and': [
            {f'analysis.components.{comp}': {'$exists': True}}
            for comp in all_expected_components
        ]
    })
    print(f"\nCards with all 20 components: {cards_with_all_components}")
    
    # 9. Check for any recent task completions
    tasks = get_mongodb_collection('swarm_tasks')
    recent_completed_tasks = tasks.count_documents({
        'status': 'completed',
        'completed_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
    })
    print(f"Tasks completed today: {recent_completed_tasks}")
    
    # 10. Recommend the best counting method
    print("\n=== RECOMMENDATIONS ===")
    print("Based on the analysis above, the most accurate count would be:")
    print("1. Cards with analysis.components that exist and are not empty")
    print("2. Or cards with analysis.component_count > 0")
    print("3. Or cards with analysis.fully_analyzed = True")
    
    return {
        'total_cards': total_cards,
        'current_logic': current_logic_count,
        'with_components': cards_with_components,
        'with_component_count': cards_with_component_count,
        'fully_analyzed_new': fully_analyzed_count,
        'completed_at_new': analysis_completed_at_count,
        'all_components': cards_with_all_components
    }

if __name__ == "__main__":
    results = analyze_card_counts()
    print(f"\nSummary: {results}")
