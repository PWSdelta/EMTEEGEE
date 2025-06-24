"""
Test script to verify the new home page stats functions work correctly.
Run this with: python test_home_stats.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.utils import get_home_page_stats, get_recent_cards_with_analysis

def test_home_stats():
    """Test the home page statistics functions"""
    
    print("Testing Home Page Statistics")
    print("=" * 50)
    
    # Test stats function
    try:
        stats = get_home_page_stats()
        print("✅ get_home_page_stats() executed successfully")
        print(f"📊 Stats: {stats}")
        print()
        
        # Validate stats structure
        required_keys = ['total_cards', 'fully_analyzed', 'in_process', 'analyzed_today']
        for key in required_keys:
            if key in stats:
                print(f"✅ {key}: {stats[key]}")
            else:
                print(f"❌ Missing key: {key}")
        
    except Exception as e:
        print(f"❌ Error in get_home_page_stats(): {e}")
    
    print("\n" + "=" * 50)
    
    # Test recent cards function
    try:
        recent_cards = get_recent_cards_with_analysis(limit=10)  # Test with smaller limit
        print("✅ get_recent_cards_with_analysis() executed successfully")
        print(f"📋 Found {len(recent_cards)} recent cards with analysis")
        
        if recent_cards:
            print("\nSample cards:")
            for i, card in enumerate(recent_cards[:3]):  # Show first 3
                name = card.get('name', 'Unknown')
                components_count = len(card.get('analysis', {}).get('components', {}))
                print(f"  {i+1}. {name} ({components_count} components)")
        
    except Exception as e:
        print(f"❌ Error in get_recent_cards_with_analysis(): {e}")
    
    print("\n" + "=" * 50)
    print("Test Complete!")

if __name__ == "__main__":
    test_home_stats()
