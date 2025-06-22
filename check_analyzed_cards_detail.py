#!/usr/bin/env python3
"""Check the detailed structure of analyzed cards."""

import os
import sys
import django
from pymongo import MongoClient

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings

def check_analyzed_cards():
    # Connect to database
    client = MongoClient(settings.MONGODB_SETTINGS['host'])
    db = client['emteegee_dev']
    cards = db.cards
    
    # Get a sample of fully analyzed cards
    fully_analyzed = list(cards.find({'analysis.fully_analyzed': True}).limit(3))
    
    for i, card in enumerate(fully_analyzed):
        print(f"\n=== CARD {i+1}: {card.get('name', 'Unknown')} ===")
        
        # Check top-level fields
        top_fields = ['name', 'mana_cost', 'type_line', 'oracle_text']
        for field in top_fields:
            if field in card:
                print(f"{field}: {card[field]}")
        
        # Check analysis structure
        if 'analysis' in card:
            analysis = card['analysis']
            print(f"\nAnalysis keys: {list(analysis.keys())}")
              # Check specific analysis components
            if 'components' in analysis:
                components = analysis['components']
                if isinstance(components, dict):
                    print(f"Number of analysis components: {len(components)}")
                    
                    # Show first few components
                    for j, (key, comp) in enumerate(list(components.items())[:3]):
                        comp_type = comp.get('type', 'Unknown') if isinstance(comp, dict) else 'Unknown'
                        comp_title = comp.get('title', key) if isinstance(comp, dict) else key
                        print(f"  Component {j+1}: {comp_type} - {comp_title}")
                        if isinstance(comp, dict) and 'content' in comp:
                            content_preview = comp['content'][:100] + "..." if len(comp['content']) > 100 else comp['content']
                            print(f"    Content preview: {content_preview}")
                        elif isinstance(comp, str):
                            content_preview = comp[:100] + "..." if len(comp) > 100 else comp
                            print(f"    Content preview: {content_preview}")
                else:
                    print(f"Components structure: {type(components)}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    check_analyzed_cards()
