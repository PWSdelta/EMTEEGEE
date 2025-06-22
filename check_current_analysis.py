#!/usr/bin/env python3
"""Check current analysis status and sample results."""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json

# Load environment variables
load_dotenv()

def check_analysis_status():
    # Connect to remote MongoDB
    client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
    db = client['emteegee']
    cards = db.cards
    
    # Get analysis status counts
    total_cards = cards.count_documents({})
    completed = cards.count_documents({'analysis_status': 'completed'})
    in_progress = cards.count_documents({'analysis_status': 'in_progress'})
    pending = cards.count_documents({'analysis_status': 'pending'})
    
    print(f"=== ANALYSIS STATUS ===")
    print(f"Total cards: {total_cards}")
    print(f"Completed: {completed}")
    print(f"In progress: {in_progress}")
    print(f"Pending: {pending}")
    print(f"Progress: {completed/total_cards*100:.1f}%")
    
    # Get sample of completed cards
    print(f"\n=== SAMPLE COMPLETED CARDS ===")
    completed_cards = list(cards.find(
        {'analysis_status': 'completed'}, 
        {'name': 1, 'mana_cost': 1, 'type_line': 1, 'analysis': 1}
    ).limit(3))
    
    for i, card in enumerate(completed_cards):
        print(f"\n--- Card {i+1}: {card.get('name', 'Unknown')} ---")
        print(f"Mana Cost: {card.get('mana_cost', 'N/A')}")
        print(f"Type: {card.get('type_line', 'N/A')}")
        
        if 'analysis' in card:
            analysis = card['analysis']
            print(f"Analysis keys: {list(analysis.keys())}")
            
            # Show specific analysis components
            if 'commander_viability' in analysis:
                print(f"Commander Viability: {analysis['commander_viability']}")
            if 'power_level' in analysis:
                print(f"Power Level: {analysis['power_level']}")
            if 'synergy_tags' in analysis:
                tags = analysis['synergy_tags']
                if isinstance(tags, list):
                    print(f"Synergy Tags: {', '.join(tags[:5])}")
                else:
                    print(f"Synergy Tags: {tags}")
            if 'strategic_analysis' in analysis:
                strategic = analysis['strategic_analysis']
                if len(strategic) > 200:
                    print(f"Strategic Analysis: {strategic[:197]}...")
                else:
                    print(f"Strategic Analysis: {strategic}")

if __name__ == "__main__":
    check_analysis_status()
