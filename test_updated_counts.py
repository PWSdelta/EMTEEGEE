#!/usr/bin/env python3
"""
Test the updated card counting logic
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

# Test the updated counting logic
print("=== TESTING UPDATED CARD COUNTING LOGIC ===")
status = enhanced_swarm.get_enhanced_swarm_status()

print(f"Total workers: {status['workers']['total']}")
print(f"Active workers: {status['workers']['active']}")
print(f"Total cards: {status['cards']['total']}")
print(f"Analyzed cards: {status['cards']['analyzed']}")
print(f"Completion rate: {status['cards']['completion_rate']}")
print(f"High priority pending: {status['cards']['high_priority_pending']}")

print("\n=== DETAILED BREAKDOWN ===")
print("This should now show the accurate count of analyzed cards!")
