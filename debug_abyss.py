#!/usr/bin/env python3
"""Debug The Abyss page to see why it shows 0 cards."""

import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def main():
    print("🕳️ Debugging The Abyss Page")
    print("=" * 50)
    
    try:
        cards_collection = get_cards_collection()
        
        # Test basic query (no filters)
        total_cards = cards_collection.count_documents({})
        print(f"📊 Total cards in database: {total_cards:,}")
        
        if total_cards > 0:
            # Test the default sort
            sample_cards = list(cards_collection.find({}).limit(5))
            print(f"\n🃏 Sample cards with default query:")
            for i, card in enumerate(sample_cards, 1):
                name = card.get('name', 'Unknown')
                uuid = card.get('uuid', 'No UUID')
                print(f"  {i}. {name} - {uuid}")
            
            # Test basic name search
            name_search = {'name': {'$regex': 'Lightning', '$options': 'i'}}
            count_name_search = cards_collection.count_documents(name_search)
            print(f"\n🔍 Name search 'Lightning': {count_name_search:,} cards")
            
            print(f"\n✅ Database connection is working!")
        else:
            print("❌ No cards found in database!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
