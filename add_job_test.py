#!/usr/bin/env python
"""
Quick script to add a job while worker is running
"""
import os
import sys
import django

# Add the parent directory to the path
sys.path.append('c:/Users/Owner/Code/emteegee')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.job_queue import job_queue
from cards.models import get_cards_collection

# Get a random card
cards_collection = get_cards_collection()
card = cards_collection.find_one({})

if card:
    print(f"🎯 Adding job for card: {card['name']} ({card['uuid'][:8]}...)")
    job_id = job_queue.enqueue_card_analysis(card['uuid'], priority=1)
    if job_id:
        print(f"✅ Job queued successfully: {job_id}")
        
        # Show current stats
        stats = job_queue.get_queue_stats()
        print(f"📊 Queue stats: {stats}")
    else:
        print("❌ Failed to queue job")
else:
    print("❌ No cards found")
