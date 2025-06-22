#!/usr/bin/env python3
"""
Simple test for card self-reference filtering without database dependency.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.templatetags.card_filters import analyze_markdown

def test_self_reference_filtering():
    """Test that self-references are filtered out from card linking."""
    
    print("🔍 Testing Card Linking Self-Reference Exclusion")
    print("=" * 50)
    
    # Mock card data (dictionary format like from MongoDB)
    test_card = {
        'name': 'Lightning Bolt',
        'display_name': 'Lightning Bolt',
        'uuid': 'test-uuid-123'
    }
    
    # Test content with self-reference
    test_content = """
This is an analysis of [[Lightning Bolt]]. 

[[Lightning Bolt]] is a powerful spell that deals 3 damage.
It synergizes well with [[Shock]] and [[Lava Spike]].
"""
    
    print("📝 Original content:")
    print(test_content)
    print("\n" + "=" * 50)
    
    # Process with current card context
    print("🔄 Processing with self-reference filtering...")
    result = analyze_markdown(test_content, test_card)
    
    print("✨ Processed content:")
    print(result)
    print("\n" + "=" * 50)
    
    # Check results
    self_ref_count = result.count('<strong>Lightning Bolt</strong>')
    link_count = result.count('href=')
    
    print("📊 Results:")
    print(f"   • Self-references as <strong> tags: {self_ref_count}")
    print(f"   • Other card links with href: {link_count}")
    
    if self_ref_count > 0:
        print("✅ PASS: Self-references are properly excluded from linking")
    else:
        print("❌ FAIL: Self-references are still being linked")
    
    if '<a href=' not in result or 'Lightning Bolt' not in result.split('<a href=')[0] if '<a href=' in result else True:
        print("✅ PASS: Lightning Bolt is not linked")
    else:
        print("❌ MIGHT FAIL: Lightning Bolt might still be linked")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_self_reference_filtering()
