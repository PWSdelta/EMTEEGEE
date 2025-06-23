#!/usr/bin/env python3
"""Debug script to check card structure"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def check_card_structure():
    try:
        cards_collection = get_cards_collection()
        sample_card = cards_collection.find_one({})
        
        if sample_card:
            print("Sample card fields:")
            for key in sample_card.keys():
                value = sample_card[key]
                if isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {type(value).__name__} (length: {len(value)})")
                else:
                    print(f"  {key}: {value} ({type(value).__name__})")
            
            print(f"\nKey fields:")
            print(f"  _id: {sample_card.get('_id')}")
            print(f"  id: {sample_card.get('id')}")
            print(f"  uuid: {sample_card.get('uuid')}")
            print(f"  name: {sample_card.get('name')}")
            
        else:
            print("No cards found in collection")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_card_structure()
