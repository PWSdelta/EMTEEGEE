#!/usr/bin/env python3
"""
Quick test script to debug mana symbol parsing
"""
import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.templatetags.card_filters import scryfall_mana_symbols, scryfall_parse_text

# Test the functions
test_mana_cost = "{2}{W}{U}"
test_card_text = "Cycling {2}{W} ({2}{W}, Discard this card: Draw a card.)"

print("=== Testing Mana Cost ===")
print(f"Input: {test_mana_cost}")
result1 = scryfall_mana_symbols(test_mana_cost)
print(f"Output: {result1}")
print()

print("=== Testing Card Text ===")
print(f"Input: {test_card_text}")
result2 = scryfall_parse_text(test_card_text)
print(f"Output: {result2}")
print()

print("=== Testing Double Processing ===")
print("Running mana symbols twice:")
double_result = scryfall_mana_symbols(result1)
print(f"Double processed: {double_result}")
