#!/usr/bin/env python3
"""
Check what fields are in a fully analyzed card.
"""

import os
import sys
import django
from pymongo import MongoClient

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings

def check_analyzed_card_structure():
    """Check what's in a fully analyzed card."""
    try:
        # Connect to MongoDB using settings
        client = MongoClient('mongodb://localhost:27017/')
        db = client['emteegee_dev']
        
        # Find one fully analyzed card
        analyzed_card = db.cards.find_one({"analysis.fully_analyzed": True})
        
        if analyzed_card:
            print("Sample fully analyzed card structure:")
            print(f"Name: {analyzed_card.get('name', 'Unknown')}")
            print(f"ID: {analyzed_card.get('_id')}")
            
            if 'analysis' in analyzed_card:
                analysis = analyzed_card['analysis']
                print("\nAnalysis fields:")
                for key in analysis.keys():
                    value = analysis[key]
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
            else:
                print("No analysis field found!")
        else:
            print("No fully analyzed cards found!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_analyzed_card_structure()
