#!/usr/bin/env python3
"""
Quick setup script to enable EDHREC-based analysis prioritization.
Run this after importing Scryfall data to set up intelligent queue prioritization.
"""

import os
import sys
from datetime import datetime

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

def check_scryfall_data():
    """Check if Scryfall data with EDHREC rankings exists."""
    cards_collection = get_cards_collection()
    
    total_cards = cards_collection.count_documents({})
    cards_with_edhrec = cards_collection.count_documents({
        'edhrecRank': {'$exists': True, '$type': 'number'}
    })
    
    print(f"📊 Database Status:")
    print(f"   Total cards: {total_cards:,}")
    print(f"   Cards with EDHREC data: {cards_with_edhrec:,}")
    
    if cards_with_edhrec == 0:
        print(f"\n❌ No EDHREC data found!")
        print(f"   You need to run the Scryfall import first:")
        print(f"   python import_scryfall_data.py")
        return False
    
    coverage_percent = (cards_with_edhrec / total_cards) * 100
    print(f"   EDHREC coverage: {coverage_percent:.1f}%")
    
    if coverage_percent < 50:
        print(f"\n⚠️  Low EDHREC coverage ({coverage_percent:.1f}%)")
        print(f"   Consider running a more complete Scryfall import")
    else:
        print(f"\n✅ Good EDHREC coverage!")
    
    return True

def setup_edhrec_prioritization():
    """Set up EDHREC-based prioritization for the analysis queue."""
    
    print("🎯 EDHREC-BASED ANALYSIS QUEUE SETUP")
    print("=" * 45)
    
    # Check if we have Scryfall data
    if not check_scryfall_data():
        return False
    
    # Import and run the EDHREC priority manager
    try:
        from edhrec_priority_manager import EDHRECPriorityManager
        
        print(f"\n🔄 Setting up EDHREC priorities...")
        manager = EDHRECPriorityManager()
        
        # Update all priorities
        results = manager.update_all_edhrec_priorities()
        
        print(f"✅ Setup complete!")
        print(f"   Updated {results['updated_count']} cards with EDHREC priorities")
        print(f"   Priority distribution: {results['priority_distribution']}")
        
        # Show a sample of the queue
        print(f"\n🚀 Sample Priority Queue (Top 5):")
        queue = manager.get_edhrec_priority_queue(5)
        
        for i, card in enumerate(queue, 1):
            print(f"   {i}. {card['name']} (EDHREC #{card['edhrec_rank']}, Score: {card['priority_score']})")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Your analysis queue now uses EDHREC prioritization instead of random!")
        print(f"   2. Popular cards (Sol Ring, Cyclonic Rift, etc.) will be analyzed first")
        print(f"   3. Run your normal analysis process - it will auto-prioritize")
        print(f"   4. Monitor with: python edhrec_priority_manager.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing EDHREC priority manager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error setting up EDHREC priorities: {e}")
        return False

def main():
    """Main setup function."""
    success = setup_edhrec_prioritization()
    
    if success:
        print(f"\n🎉 EDHREC prioritization is now ACTIVE!")
        print(f"   Your analysis queue will prioritize popular cards over random ones.")
    else:
        print(f"\n💥 Setup failed. Check the errors above.")

if __name__ == "__main__":
    main()
