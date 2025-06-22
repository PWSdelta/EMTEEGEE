#!/usr/bin/env python3
"""Check current AI analysis status."""

import os
import sys
import django
from pymongo import MongoClient

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings

def check_analysis_status():
    # Connect directly to the correct database
    client = MongoClient(settings.MONGODB_SETTINGS['host'])
    db = client['emteegee_dev']
    cards = db.cards
    
    # Count total cards
    total = cards.count_documents({})
    print(f'Total cards: {total}')
      # Count cards with AI analysis
    analyzed = cards.count_documents({'ai_analysis': {'$exists': True, '$ne': None}})
    print(f'Cards with AI analysis: {analyzed}')
    
    # Count cards with enhancement
    enhanced = cards.count_documents({'enhancement': {'$exists': True, '$ne': None}})
    print(f'Cards with enhancement: {enhanced}')
    
    # Count completed reviews
    reviewed = cards.count_documents({'review_status': 'completed'})
    print(f'Cards with completed reviews: {reviewed}')
    
    # Count cards with analysis.fully_analyzed = true
    fully_analyzed_count = cards.count_documents({'analysis.fully_analyzed': True})
    print(f'Fully analyzed cards (analysis.fully_analyzed): {fully_analyzed_count}')
    
    # Check analysis field structure
    with_analysis = cards.count_documents({'analysis': {'$exists': True}})
    print(f'Cards with analysis field: {with_analysis}')
    
    # Show sample
    sample = cards.find_one({'ai_analysis': {'$exists': True}})
    if sample:
        print(f'Sample analyzed card: {sample.get("name", "Unknown")}')

if __name__ == "__main__":
    check_analysis_status()
