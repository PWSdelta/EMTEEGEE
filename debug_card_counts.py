#!/usr/bin/env python3
"""
Database Diagnostic Script - Check card analysis status
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.enhanced_swarm_manager import enhanced_swarm

def check_database_status():
    """Check the current state of the card database"""
    print("🔍 DATABASE DIAGNOSTIC REPORT")
    print("=" * 50)
    
    # Total cards
    total_cards = enhanced_swarm.cards.count_documents({})
    print(f"📊 Total cards in database: {total_cards:,}")
    
    # Fully analyzed cards
    fully_analyzed = enhanced_swarm.cards.count_documents({
        'analysis.fully_analyzed': True
    })
    print(f"✅ Fully analyzed cards: {fully_analyzed:,}")
    
    # Cards with some analysis
    partial_analysis = enhanced_swarm.cards.count_documents({
        'analysis.component_count': {'$gt': 0, '$lt': 20}
    })
    print(f"⚠️  Partially analyzed cards: {partial_analysis:,}")
    
    # Unanalyzed cards (what workers should get)
    unanalyzed = enhanced_swarm.cards.count_documents({
        '$or': [
            {'analysis.fully_analyzed': {'$ne': True}},
            {'analysis': {'$exists': False}},
            {'analysis.component_count': {'$lt': 20}}
        ]
    })
    print(f"❌ Unanalyzed/incomplete cards: {unanalyzed:,}")
    
    # Test the random selection pipeline
    print(f"\n🎲 TESTING RANDOM SELECTION...")
    pipeline = [
        {
            '$match': {
                '$or': [
                    {'analysis.fully_analyzed': {'$ne': True}},
                    {'analysis': {'$exists': False}},
                    {'analysis.component_count': {'$lt': 20}}
                ]
            }
        },
        {'$sample': {'size': 5}},  # Get 5 random cards
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'analysis.fully_analyzed': 1,
                'analysis.component_count': 1
            }
        }
    ]
    
    sample_cards = list(enhanced_swarm.cards.aggregate(pipeline))
    print(f"📋 Random sample of available cards:")
    for i, card in enumerate(sample_cards, 1):
        name = card.get('name', 'Unknown')
        card_id = str(card['_id'])
        analyzed = card.get('analysis', {}).get('fully_analyzed', False)
        component_count = card.get('analysis', {}).get('component_count', 0)
        print(f"   {i}. {name[:30]:<30} | ID: {card_id[:8]}... | Analyzed: {analyzed} | Components: {component_count}")
    
    # Check tasks
    print(f"\n📋 TASK STATUS")
    pending_tasks = enhanced_swarm.tasks.count_documents({'status': 'assigned'})
    completed_tasks = enhanced_swarm.tasks.count_documents({'status': 'completed'})
    print(f"⏳ Pending tasks: {pending_tasks}")
    print(f"✅ Completed tasks: {completed_tasks}")
    
    # Check workers
    print(f"\n👥 WORKER STATUS")
    active_workers = enhanced_swarm.workers.count_documents({'status': 'active'})
    total_workers = enhanced_swarm.workers.count_documents({})
    print(f"� Active workers: {active_workers}")
    print(f"📝 Total registered workers: {total_workers}")
    
    print(f"\n🎯 CONCLUSION:")
    if unanalyzed > 0:
        print(f"✅ There are {unanalyzed:,} cards available for analysis")
        print(f"🔍 Workers should be getting work assignments")
        if len(sample_cards) > 0:
            print(f"🎲 Random selection is working - found {len(sample_cards)} sample cards")
        else:
            print(f"❌ Random selection pipeline failed - no cards returned")
    else:
        print(f"🎉 All cards are fully analyzed!")
        print(f"💤 No work available for workers")

if __name__ == "__main__":
    check_database_status()