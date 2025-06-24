#!/usr/bin/env python3
"""
Test the synthesis system on the beast laptop.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')

import django
django.setup()

from synthesis_manager import synthesis_manager

def main():
    print("🔍 Testing Synthesis System")
    print("=" * 50)
    
    # Check if this is the right machine
    print(f"Hostname: {synthesis_manager.hostname}")
    print(f"Is Beast Laptop: {synthesis_manager.is_beast_laptop}")
    print(f"Model: {synthesis_manager.model}")
    
    if not synthesis_manager.should_synthesize_on_this_machine():
        print("\n⚠️  This machine is not configured to run synthesis.")
        print("Only the beast laptop should generate synthesis reports.")
        return
    
    # Get statistics
    print("\n📊 Current Statistics:")
    stats = synthesis_manager.get_synthesis_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if stats['cards_ready_for_synthesis'] == 0:
        print("\n✅ No cards ready for synthesis - all caught up!")
        return
    
    # Find some cards to synthesize
    print(f"\n🎯 Finding cards ready for synthesis...")
    ready_cards = synthesis_manager.find_cards_ready_for_synthesis(3)
    
    if not ready_cards:
        print("No cards found - this is strange given the stats above.")
        return
    
    print(f"Found {len(ready_cards)} cards ready for synthesis:")
    for i, card in enumerate(ready_cards, 1):
        name = card.get('name', 'Unknown')
        rank = card.get('edhrecRank', 'N/A')
        component_count = card.get('component_count', 0)
        print(f"  {i}. {name} (EDHREC #{rank}, {component_count} components)")
    
    # Run a small test batch
    print(f"\n🚀 Running synthesis batch (3 cards)...")
    results = synthesis_manager.run_synthesis_batch(3)
    
    print("\n📈 Synthesis Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    if results.get('success', 0) > 0:
        print(f"\n✅ Success! Generated {results['success']} complete analyses.")
        print("You can now view these cards to see their synthesized analyses.")
    
    # Show updated stats
    print("\n📊 Updated Statistics:")
    updated_stats = synthesis_manager.get_synthesis_stats()
    for key, value in updated_stats.items():
        print(f"  {key}: {value}")

if __name__ == '__main__':
    main()
