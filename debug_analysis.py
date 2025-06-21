#!/usr/bin/env python
"""
Debug script to check card analysis status
"""
import os
import sys
import django

sys.path.append('c:/Users/Owner/Code/emteegee')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection
from cards.job_queue import job_queue

# Check cards collection
cards_collection = get_cards_collection()

# Sample a few cards
print("🔍 Checking card analysis status...")
sample_cards = list(cards_collection.find().limit(5))

for card in sample_cards:
    analysis = card.get('analysis', {})
    print(f"Card: {card['name'][:20]:<20} | UUID: {card['uuid'][:8]} | Analysis: {analysis}")

# Check queue
stats = job_queue.get_queue_stats()
print(f"\n📊 Queue stats: {stats}")

# Check total cards with different analysis states
total = cards_collection.count_documents({})
no_analysis = cards_collection.count_documents({"analysis": {"$exists": False}})
not_fully_analyzed = cards_collection.count_documents({"analysis.fully_analyzed": {"$ne": True}})

print(f"\n📈 Card Statistics:")
print(f"   Total cards: {total:,}")
print(f"   No analysis field: {no_analysis:,}")
print(f"   Not fully analyzed: {not_fully_analyzed:,}")

# Try simple queue method
print(f"\n🎯 Testing simple queue (limit 2)...")
jobs_queued = job_queue.queue_all_unanalyzed_simple(max_cards=2)
print(f"   Jobs queued: {jobs_queued}")

# Final stats
final_stats = job_queue.get_queue_stats()
print(f"   Final queue: {final_stats}")
