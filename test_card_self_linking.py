#!/usr/bin/env python3
"""
Test the updated card linking functionality to ensure self-references are excluded.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import Card
from cards.templatetags.card_filters import analyze_markdown

def test_card_linking_exclusion():
    print("🔍 Testing Card Linking Self-Reference Exclusion")
    print("=" * 50)
    
    # Find a card to test with
    test_card = Card.objects.filter(name__icontains='lightning').first()
    
    if not test_card:
        print("❌ No test card found")
        return
    
    print(f"📋 Testing with card: {test_card.name}")
    
    # Test content that includes the card's own name
    test_content = f"""
This is a test analysis for [[{test_card.name}]].

Some other cards that work well with [[{test_card.name}]] include:
- [[Lightning Helix]]
- [[Counterspell]]
- [[{test_card.name}]] itself is powerful

[[{test_card.name}]] synergizes with many other cards.
"""
    
    print("\n📝 Test content:")
    print(test_content)
    
    # Test without current card (old behavior)
    print("\n🔄 Without current card exclusion:")
    result_without = analyze_markdown(test_content)
    print(result_without)
    
    # Test with current card exclusion (new behavior)
    print("\n✨ With current card exclusion:")
    result_with = analyze_markdown(test_content, test_card)
    print(result_with)
    
    # Count self-references
    self_ref_count_without = result_without.count(f'href="/card/{test_card.uuid}/')
    self_ref_count_with = result_with.count(f'href="/card/{test_card.uuid}/')
    
    print(f"\n📊 Results:")
    print(f"   Without exclusion: {self_ref_count_without} self-references found")
    print(f"   With exclusion: {self_ref_count_with} self-references found")
    
    if self_ref_count_with < self_ref_count_without:
        print("✅ SUCCESS: Self-references have been reduced!")
    else:
        print("❌ ISSUE: Self-references were not properly excluded")

if __name__ == "__main__":
    test_card_linking_exclusion()
