#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

# Get a card
cards = get_cards_collection()
card = cards.find_one()

if card:
    print(f"Card name: {card['name']}")
    print(f"Card UUID: {card['uuid']}")
    print(f"URL: http://localhost:8000/cards/{card['uuid']}/")
    
    # Check if it has analysis
    analysis = card.get('analysis', {})
    if analysis:
        print(f"Analysis components: {analysis.get('component_count', 0)}")
        print(f"Fully analyzed: {analysis.get('fully_analyzed', False)}")
else:
    print("No cards found")
