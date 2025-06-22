#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_decks_collection

decks_collection = get_decks_collection()
total = decks_collection.count_documents({})
print(f"Total decks remaining: {total}")

samples = list(decks_collection.find({}, {'name': 1, 'stats.total_count': 1}).limit(5))
print("Sample decks:")
for deck in samples:
    name = deck.get('name', 'Unknown')
    count = deck.get('stats', {}).get('total_count', 0)
    print(f"  {name}: {count} cards")
