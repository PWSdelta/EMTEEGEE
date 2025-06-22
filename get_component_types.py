#!/usr/bin/env python3
"""Get all component types from analyzed cards."""

import os
import sys
import django
from pymongo import MongoClient

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings

def get_component_types():
    # Connect to database
    client = MongoClient(settings.MONGODB_SETTINGS['host'])
    db = client['emteegee_dev']
    cards = db.cards
    
    # Get one fully analyzed card
    card = cards.find_one({'analysis.fully_analyzed': True})
    
    if card and 'analysis' in card and 'components' in card['analysis']:
        components = card['analysis']['components']
        print(f"Card: {card.get('name', 'Unknown')}")
        print(f"Component types ({len(components)} total):")
        
        for i, (key, comp) in enumerate(components.items(), 1):
            print(f"{i:2d}. {key}")
    else:
        print("No analyzed card found")

if __name__ == "__main__":
    get_component_types()
