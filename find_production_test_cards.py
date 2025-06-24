#!/usr/bin/env python3
"""
Production server script to find cards with rich analysis components.
Run this ON YOUR SERVER after deployment to find good test cards.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def find_production_test_cards():
    print("🔍 PRODUCTION: Searching for cards with rich analysis...")
    print("=" * 60)
    
    cards = get_cards_collection()
    
    # Get basic stats
    total_cards = cards.count_documents({})
    analyzed_cards = cards.count_documents({'analysis.fully_analyzed': True})
    
    print(f"📊 Production Database Stats:")
    print(f"   Total Cards: {total_cards:,}")
    print(f"   Analyzed Cards: {analyzed_cards:,}")
    
    # Search for Sol Ring specifically (popular card likely to be analyzed)
    sol_ring = cards.find_one({'name': 'Sol Ring'})
    if sol_ring:
        analysis = sol_ring.get('analysis', {})
        uuid = sol_ring.get('uuid', '')
        component_count = analysis.get('component_count', 0)
        
        print(f"\n🎯 Sol Ring Found!")
        print(f"   UUID: {uuid}")
        print(f"   Component Count: {component_count}")
        print(f"   🌐 Production URL: https://yourdomain.com/card/{uuid}/")
        
        # Check for actual components data
        components = analysis.get('components', {})
        if isinstance(components, dict) and components:
            print(f"   ✅ Has {len(components)} components with data")
            sample_key = next(iter(components.keys()))
            sample_comp = components[sample_key]
            if isinstance(sample_comp, dict) and 'content' in sample_comp:
                content_length = len(sample_comp['content'])
                print(f"   📝 Sample component '{sample_key}': {content_length} chars")
        else:
            print(f"   ⚠️  Components structure needs investigation")
    
    # Find cards with highest component counts
    print(f"\n🏆 Top Cards by Component Count:")
    high_component_cards = list(cards.find({
        'analysis.component_count': {'$gte': 15}
    }).sort([('analysis.component_count', -1)]).limit(10))
    
    if high_component_cards:
        for i, card in enumerate(high_component_cards, 1):
            name = card.get('name', 'Unknown')
            uuid = card.get('uuid', '')
            analysis = card.get('analysis', {})
            component_count = analysis.get('component_count', 0)
            
            print(f"\n{i}. {name}")
            print(f"   UUID: {uuid}")
            print(f"   Components: {component_count}/20")
            print(f"   🌐 URL: https://yourdomain.com/card/{uuid}/")
            
            # Check for synthesis
            complete_analysis = card.get('complete_analysis')
            if complete_analysis:
                print(f"   ✨ Has synthesis: {len(complete_analysis)} chars")
            
            # Sample first few component keys if available
            components = analysis.get('components', {})
            if isinstance(components, dict) and components:
                comp_keys = list(components.keys())[:3]
                print(f"   🔧 Sample components: {comp_keys}")
    else:
        print("   No cards found with 15+ components")
    
    # Also search for commonly analyzed cards
    popular_cards = [
        'Lightning Bolt', 'Counterspell', 'Birds of Paradise', 
        'Serra Angel', 'Black Lotus', 'Ancestral Recall'
    ]
    
    print(f"\n🎴 Checking Popular Cards:")
    for card_name in popular_cards:
        card = cards.find_one({'name': card_name})
        if card:
            analysis = card.get('analysis', {})
            component_count = analysis.get('component_count', 0)
            uuid = card.get('uuid', '')
            
            if component_count > 5:  # Has some analysis
                print(f"   ✅ {card_name}: {component_count} components")
                print(f"      🌐 https://yourdomain.com/card/{uuid}/")
    
    print(f"\n🚀 DEPLOYMENT TEST INSTRUCTIONS:")
    print(f"1. Deploy the card detail improvements to your server")
    print(f"2. Visit any of the URLs above")
    print(f"3. Look for:")
    print(f"   ✅ Full component text (not truncated)")
    print(f"   ✅ Proper markdown formatting") 
    print(f"   ✅ Individual expand/collapse buttons")
    print(f"   ✅ Enhanced styling and readability")
    
    return True

if __name__ == "__main__":
    find_production_test_cards()
