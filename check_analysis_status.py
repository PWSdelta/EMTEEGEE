#!/usr/bin/env python3
"""
Check card analysis completion status
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongodb_uri = os.getenv('MONGODB_CONNECTION_STRING')
client = MongoClient(mongodb_uri)
db = client.emteegee_dev
cards = db.cards

print('Analyzing card completion status...')

# Count total cards
total_cards = cards.count_documents({})
print(f'Total cards: {total_cards}')

# Count cards with no analysis field
no_analysis = cards.count_documents({'analysis': {'$exists': False}})
print(f'Cards with no analysis field: {no_analysis}')

# Count cards with no component_count
no_component_count = cards.count_documents({'analysis.component_count': {'$exists': False}})
print(f'Cards with no component_count: {no_component_count}')

# Count cards with component_count < 20
incomplete = cards.count_documents({'analysis.component_count': {'$lt': 20}})
print(f'Cards with component_count < 20: {incomplete}')

# Count cards with exactly 20 components
complete = cards.count_documents({'analysis.component_count': 20})
print(f'Cards with exactly 20 components: {complete}')

# Cards needing work
cards_needing_work = cards.count_documents({
    '$or': [
        {'analysis.component_count': {'$exists': False}},
        {'analysis.component_count': {'$lt': 20}}
    ]
})
print(f'\nTotal cards needing analysis: {cards_needing_work}')

# Sample a few cards to see their structure
print('\nSample card analysis structures:')
for i, card in enumerate(cards.find({}, {'name': 1, 'analysis.component_count': 1}).limit(5)):
    component_count = card.get('analysis', {}).get('component_count', 'None')
    name = card.get('name', 'Unknown')
    print(f'  {name}: {component_count} components')

if cards_needing_work == 0:
    print('\n🎉 ALL CARDS ARE FULLY ANALYZED!')
    print('No work needed - the migration preserved all analysis data.')
else:
    print(f'\n🔧 {cards_needing_work} cards need analysis work.')
