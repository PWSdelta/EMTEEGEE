#!/usr/bin/env python3
"""
Production analysis investigation script.
Run this on your server to understand the current analysis state.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

def investigate_production_analysis():
    print("🔍 PRODUCTION ANALYSIS INVESTIGATION")
    print("=" * 50)
    
    cards = get_cards_collection()
    
    # Basic stats
    total_cards = cards.count_documents({})
    print(f"📊 Total Cards: {total_cards:,}")
    
    # Check different analysis states
    print("\n🔍 Analysis States:")
    
    # Cards with any analysis field
    cards_with_analysis_field = cards.count_documents({'analysis': {'$exists': True}})
    print(f"   Cards with 'analysis' field: {cards_with_analysis_field:,}")
    
    # Cards marked as fully analyzed (legacy flag)
    fully_analyzed_legacy = cards.count_documents({'analysis.fully_analyzed': True})
    print(f"   Cards marked fully_analyzed: {fully_analyzed_legacy:,}")
    
    # Cards with any components
    cards_with_components = cards.count_documents({'analysis.components': {'$exists': True, '$ne': {}}})
    print(f"   Cards with components: {cards_with_components:,}")
    
    # Cards with component_count field
    cards_with_count = cards.count_documents({'analysis.component_count': {'$exists': True}})
    print(f"   Cards with component_count: {cards_with_count:,}")
    
    # Sample analysis structure
    print("\n🔬 Sample Analysis Structures:")
    sample_cards = list(cards.find({'analysis': {'$exists': True}}).limit(3))
    
    for i, card in enumerate(sample_cards, 1):
        name = card.get('name', 'Unknown')
        analysis = card.get('analysis', {})
        
        print(f"\n{i}. {name}:")
        print(f"   Analysis keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'Not a dict'}")
        
        if 'components' in analysis:
            components = analysis['components']
            print(f"   Components type: {type(components)}")
            if isinstance(components, dict):
                print(f"   Component keys: {list(components.keys())[:5]}")
            elif isinstance(components, list):
                print(f"   Component count: {len(components)}")
                if components:
                    print(f"   First component: {type(components[0])}")
        
        if 'component_count' in analysis:
            print(f"   Component count: {analysis['component_count']}")
        
        if 'fully_analyzed' in analysis:
            print(f"   Fully analyzed: {analysis['fully_analyzed']}")
    
    # Check for workers or jobs
    print("\n⚙️  Worker/Job Status:")
    try:
        # Check if there are any job queues or workers
        active_jobs = cards.count_documents({'analysis.status': 'processing'})
        queued_jobs = cards.count_documents({'analysis.status': 'queued'})
        print(f"   Active jobs: {active_jobs}")
        print(f"   Queued jobs: {queued_jobs}")
    except Exception:
        print("   No job tracking found")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if fully_analyzed_legacy > 0:
        print(f"   ✅ Found {fully_analyzed_legacy} cards marked as analyzed")
        print("   🔧 These might use legacy analysis format")
        print("   📝 Check component structure and update homepage queries")
    
    if cards_with_components == 0:
        print("   ⚠️  No cards have component analysis yet")
        print("   🚀 Start analysis workers to begin generating components")
        print("   📋 Use: python universal_worker_enhanced.py")
    
    if cards_with_count > 0:
        print(f"   ✅ Found {cards_with_count} cards with component counts")
        print("   🔍 Investigate component structure format")
    
    print("\n🎯 NEXT STEPS:")
    print("1. If workers aren't running: Start analysis workers")
    print("2. If legacy format: Update homepage queries for compatibility") 
    print("3. If no analysis: Begin analysis process with priority cards")
    print("4. Check worker logs for any errors or issues")

if __name__ == "__main__":
    investigate_production_analysis()
