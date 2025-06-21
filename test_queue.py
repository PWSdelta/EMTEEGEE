#!/usr/bin/env python
"""
Test script to queue a single card for analysis
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.job_queue import job_queue
from cards.models import get_cards_collection

def test_queue():
    print("🧪 Testing job queue functionality...")
    
    # Get a card that needs analysis
    cards_collection = get_cards_collection()
    card = cards_collection.find_one({
        '$or': [
            {'analysis.fully_analyzed': {'$ne': True}},
            {'analysis': {'$exists': False}}
        ]
    })
    
    if card:
        print(f"✅ Found card: {card['name']}")
        print(f"📝 UUID: {card['uuid']}")
        
        # Check current analysis status
        analysis = card.get('analysis', {})
        print(f"📊 Current analysis: {analysis.get('component_count', 0)}/20 components")
        
        # Queue the job
        job_id = job_queue.enqueue_card_analysis(card['uuid'])
        
        if job_id:
            print(f"🎯 Successfully queued job: {job_id}")
            
            # Check queue status
            stats = job_queue.get_queue_stats()
            print(f"📈 Queue stats: {stats}")
            
            return True
        else:
            print("❌ Failed to queue job")
            return False
    else:
        print("⚠️ No unanalyzed cards found")
        return False

if __name__ == "__main__":
    test_queue()
