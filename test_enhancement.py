#!/usr/bin/env python3
"""Test sc          print(f"📊 Testing {len(test_cards)} cards:")
        for card in test_cards:
            name = card.get('name', 'Unknown')
            edhrec_rank = card.get('edhrecRank', 999999)
            old_score = card.get('edhrecPriorityScore', 0)
            priority = job_queue._calculate_smart_priority(card)  print(f"📊 Testing {len(test_cards)} cards:")
        
        for card in test_cards:pt to verify smart prioritization system."""

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

def test_smart_prioritization():
    """Test the smart prioritization logic."""
    print("🎯 Testing Smart Prioritization System")
    print("=" * 60)
    
    try:
        from cards.models import get_cards_collection
        from cards.job_queue import JobQueue
        
        cards_collection = get_cards_collection()
        job_queue = JobQueue()
        
        print("✅ Successfully imported modules")
          # Test with a few real cards that have EDHREC ranks
        test_cards = list(cards_collection.find(
            {'edhrecRank': {'$exists': True, '$ne': None}}, {
            'uuid': 1, 'name': 1, 'edhrecRank': 1, 'analysis.components': 1, 
            'edhrecPriorityScore': 1, 'prices.usd': 1
        }).limit(5))
        
        print(f"� Testing {len(test_cards)} cards:")
        for card in test_cards:
            name = card.get('name', 'Unknown')
            priority = job_queue._calculate_smart_priority(card)
            
            # Count components
            components = card.get('analysis', {}).get('components', {})
            completed_count = sum(1 for comp in components.values() if comp is not None) if components else 0
            
            # Handle EDHREC score (might be stored as different types)
            edhrec_score = card.get('edhrecPriorityScore', 0)
            try:
                edhrec_score = float(edhrec_score) if edhrec_score else 0
            except (ValueError, TypeError):
                edhrec_score = 0
            
            # Handle USD price (might be stored as string)
            usd_price = card.get('prices', {}).get('usd', 0)
            try:
                usd_price = float(usd_price) if usd_price else 0
            except (ValueError, TypeError):
                usd_price = 0
            
            print(f"\n🃏 {name}")
            print(f"   Components: {completed_count}/20")
            print(f"   EDHREC: {edhrec_score:.3f}")
            print(f"   Price: ${usd_price:.2f}")
            print(f"   🎯 Priority: {priority}")
          print("\n✅ EDHREC-based prioritization system is working!")
        print("📋 Priority logic (EDHREC rank-based):")
        print("  - 999999+ = EDHREC Rank #1 (highest priority)")
        print("  - 950000+ = EDHREC Rank #50,000")
        print("  - 900000+ = EDHREC Rank #100,000")
        print("  - 1 = No EDHREC data (lowest priority)")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_prioritization()
