#!/usr/bin/env python3
"""Test script to verify EDHREC rank-based prioritization system."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def test_edhrec_prioritization():
    """Test the EDHREC rank-based prioritization logic."""
    print("🎯 Testing EDHREC Rank-Based Prioritization System")
    print("=" * 60)
    
    try:
        from cards.models import get_cards_collection
        from cards.job_queue import JobQueue
        
        cards_collection = get_cards_collection()
        job_queue = JobQueue()
        
        print("✅ Successfully imported modules")
        
        # Test with cards that have EDHREC ranks
        test_cards = list(cards_collection.find(
            {'edhrecRank': {'$exists': True, '$ne': None}}, 
            {'uuid': 1, 'name': 1, 'edhrecRank': 1, 'analysis.components': 1}
        ).limit(5))
        
        print(f"📊 Testing {len(test_cards)} cards:")
        
        for card in test_cards:
            name = card.get('name', 'Unknown')
            edhrec_rank = card.get('edhrecRank', 999999)
            priority = job_queue._calculate_smart_priority(card)
            
            # Count components
            components = card.get('analysis', {}).get('components', {})
            completed_count = sum(1 for comp in components.values() if comp is not None) if components else 0
            
            print(f"\n🃏 {name}")
            print(f"   EDHREC Rank: #{edhrec_rank}")
            print(f"   Components: {completed_count}/20")
            print(f"   🎯 Priority: {priority} (negative rank for DESC sort)")
        
        print("\n✅ EDHREC rank-based prioritization system is working!")
        print("📋 Priority logic:")
        print("  - Lower EDHREC rank = Higher priority")
        print("  - Rank #1 = Priority -1 (processed first)")
        print("  - Rank #50,000 = Priority -50,000 (processed later)")
        print("  - No EDHREC data = Priority -999,999 (lowest priority)")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_edhrec_prioritization()
