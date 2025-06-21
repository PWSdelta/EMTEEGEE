#!/usr/bin/env python3
"""
EDHREC-Based Analysis Queue Prioritization for EMTEEGEE
Uses EDHREC popularity rankings to intelligently queue cards for analysis.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import Counter
from pymongo import UpdateOne

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

class EDHRECPriorityManager:
    """Manages analysis queue prioritization based on EDHREC rankings."""
    
    def __init__(self):
        self.cards_collection = get_cards_collection()
        
        # EDHREC-based priority tiers
        self.priority_tiers = {
            'legendary': {'min_rank': 1, 'max_rank': 50, 'priority': 'legendary', 'score': 1000},
            'top_tier': {'min_rank': 51, 'max_rank': 200, 'priority': 'critical', 'score': 800},
            'high_tier': {'min_rank': 201, 'max_rank': 500, 'priority': 'high', 'score': 600},
            'popular': {'min_rank': 501, 'max_rank': 1000, 'priority': 'medium', 'score': 400},
            'notable': {'min_rank': 1001, 'max_rank': 3000, 'priority': 'low', 'score': 200},
            'niche': {'min_rank': 3001, 'max_rank': 10000, 'priority': 'very_low', 'score': 50}
        }
        
    def calculate_edhrec_priority_score(self, card_name: str) -> Dict[str, any]:
        """Calculate priority score based on EDHREC ranking and other factors."""
        card = self.cards_collection.find_one({'name': card_name})
        if not card:
            return {'error': f'Card "{card_name}" not found'}
        
        result = {
            'card_name': card_name,
            'edhrec_rank': card.get('edhrecRank'),
            'base_score': 0,
            'bonus_points': {},
            'total_score': 0,
            'priority_tier': 'unranked',
            'priority_level': 'minimal',
            'reasons': []
        }
        
        edhrec_rank = card.get('edhrecRank')
        
        # Base score from EDHREC ranking
        if edhrec_rank:
            for tier_name, tier_info in self.priority_tiers.items():
                if tier_info['min_rank'] <= edhrec_rank <= tier_info['max_rank']:
                    result['base_score'] = tier_info['score']
                    result['priority_tier'] = tier_name
                    result['priority_level'] = tier_info['priority']
                    result['reasons'].append(f"EDHREC rank #{edhrec_rank} ({tier_name} tier)")
                    break
            else:
                # Very low priority for cards ranked lower than 10,000
                if edhrec_rank > 10000:
                    result['base_score'] = 10
                    result['priority_tier'] = 'deep_niche'
                    result['priority_level'] = 'minimal'
                    result['reasons'].append(f"EDHREC rank #{edhrec_rank} (deep niche)")
        else:
            result['reasons'].append("No EDHREC ranking available")
        
        # Bonus points for various factors
        bonuses = result['bonus_points']
        
        # Relationship bonus (cards with connections to other cards)
        all_parts = card.get('allParts', [])
        if all_parts:
            relationship_bonus = len(all_parts) * 25
            bonuses['relationships'] = relationship_bonus
            result['reasons'].append(f"+{relationship_bonus} for {len(all_parts)} card relationships")
        
        # Rarity bonus (higher rarity often means more complex/interesting effects)
        rarity = card.get('rarity', '').lower()
        rarity_bonuses = {'mythic': 100, 'rare': 50, 'uncommon': 20, 'common': 0}
        if rarity in rarity_bonuses:
            rarity_bonus = rarity_bonuses[rarity]
            if rarity_bonus > 0:
                bonuses['rarity'] = rarity_bonus
                result['reasons'].append(f"+{rarity_bonus} for {rarity} rarity")
        
        # Format availability bonus (more formats = more interest)
        legalities = card.get('legalities', {})
        legal_formats = sum(1 for status in legalities.values() if status == 'legal')
        if legal_formats >= 5:
            format_bonus = legal_formats * 10
            bonuses['format_availability'] = format_bonus
            result['reasons'].append(f"+{format_bonus} for legal in {legal_formats} formats")
        
        # Commander-specific bonuses
        is_legendary_creature = False
        type_line = card.get('type', '').lower()
        if 'legendary' in type_line and 'creature' in type_line:
            is_legendary_creature = True
            bonuses['commander_eligible'] = 150
            result['reasons'].append("+150 for being a potential Commander")
        
        # Popular card types bonus
        if 'instant' in type_line or 'sorcery' in type_line:
            bonuses['spell'] = 30
            result['reasons'].append("+30 for being a spell (high impact)")
        elif 'artifact' in type_line and 'equipment' in type_line:
            bonuses['equipment'] = 40
            result['reasons'].append("+40 for being equipment (EDH staple type)")
        elif 'enchantment' in type_line:
            bonuses['enchantment'] = 25
            result['reasons'].append("+25 for being an enchantment")
        
        # Keyword mechanics bonus (more complex cards)
        keywords = card.get('keywords', [])
        if len(keywords) >= 3:
            keyword_bonus = len(keywords) * 15
            bonuses['keywords'] = keyword_bonus  
            result['reasons'].append(f"+{keyword_bonus} for {len(keywords)} keyword abilities")
        
        # Recent set bonus (newer cards get slight priority)
        released_at = card.get('releasedAt')
        if released_at and released_at >= '2023-01-01':  # Cards from 2023 onwards
            bonuses['recent'] = 50
            result['reasons'].append("+50 for being from a recent set")
        
        # Calculate total score
        total_bonus = sum(bonuses.values())
        result['total_score'] = result['base_score'] + total_bonus
        
        return result
    
    def update_all_edhrec_priorities(self) -> Dict[str, any]:
        """Update EDHREC-based priorities for all cards without analysis."""
        print("🎯 Updating EDHREC-based analysis priorities...")
        
        # Get all cards that need analysis and have EDHREC rankings
        unanalyzed_cards = list(self.cards_collection.find({
            '$and': [
                {'analysis': {'$exists': False}},
                {'analysisRequested': {'$ne': True}},
                {'edhrecRank': {'$exists': True, '$type': 'number'}}
            ]        }, {'name': 1, 'edhrecRank': 1}))
        
        print(f"Found {len(unanalyzed_cards)} unanalyzed cards with EDHREC rankings")
        
        updated_count = 0
        priority_distribution = Counter()
        score_ranges = Counter()
        
        # Process cards in batches for optimal performance
        batch_size = 2357
        
        for i in range(0, len(unanalyzed_cards), batch_size):
            batch = unanalyzed_cards[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(unanalyzed_cards) + batch_size - 1) // batch_size
            
            print(f"Processing EDHREC priority batch {batch_num}/{total_batches} ({len(batch)} cards)")
            
            # Prepare bulk operations for this batch
            bulk_operations = []
            
            for card_doc in batch:
                card_name = card_doc['name']
                priority_result = self.calculate_edhrec_priority_score(card_name)
                
                if 'error' not in priority_result:
                    total_score = priority_result['total_score']
                    priority_level = priority_result['priority_level']
                    
                    # Prepare bulk update operation
                    bulk_operations.append(
                        UpdateOne(
                            {'name': card_name},
                            {
                                '$set': {
                                    'edhrecPriorityScore': total_score,
                                    'edhrecPriorityLevel': priority_level,
                                    'edhrecPriorityTier': priority_result['priority_tier'],
                                    'edhrecPriorityReasons': priority_result['reasons'],
                                    'priorityUpdatedAt': datetime.now(timezone.utc).isoformat()
                                }
                            }
                        )
                    )
                    
                    updated_count += 1
                    priority_distribution[priority_level] += 1
                    
                    # Score range distribution for analysis
                    if total_score >= 800:
                        score_ranges['800+'] += 1
                    elif total_score >= 600:
                        score_ranges['600-799'] += 1
                    elif total_score >= 400:
                        score_ranges['400-599'] += 1
                    elif total_score >= 200:
                        score_ranges['200-399'] += 1
                    else:
                        score_ranges['<200'] += 1
            
            # Execute bulk operations for this batch
            if bulk_operations:
                try:
                    print(f"Executing {len(bulk_operations)} bulk priority updates for batch {batch_num}")
                    result = self.cards_collection.bulk_write(bulk_operations, ordered=False)
                    print(f"Batch {batch_num} completed: {result.modified_count} cards updated")
                except Exception as e:
                    print(f"Error in bulk update for batch {batch_num}: {e}")
                    # Fall back to individual updates for this batch if bulk fails
                    for op in bulk_operations:
                        try:
                            self.cards_collection.update_one(op._filter, op._doc)
                        except Exception as individual_error:
                            print(f"Individual update also failed: {individual_error}")
        
        
        return {
            'updated_count': updated_count,
            'priority_distribution': dict(priority_distribution),
            'score_ranges': dict(score_ranges)
        }
    
    def get_edhrec_priority_queue(self, limit: int = 25, min_score: int = 100) -> List[Dict[str, any]]:
        """Get the next highest priority cards based on EDHREC rankings."""
        priority_cards = list(self.cards_collection.find({
            '$and': [
                {'analysis': {'$exists': False}},
                {'analysisRequested': {'$ne': True}},
                {'edhrecPriorityScore': {'$gte': min_score}}
            ]
        }, {
            'name': 1, 'edhrecRank': 1, 'edhrecPriorityScore': 1, 
            'edhrecPriorityLevel': 1, 'edhrecPriorityTier': 1,
            'edhrecPriorityReasons': 1, 'type': 1, 'rarity': 1,
            'allParts': 1
        }).sort('edhrecPriorityScore', -1).limit(limit))
        
        results = []
        for card in priority_cards:
            results.append({
                'name': card['name'],
                'edhrec_rank': card.get('edhrecRank'),
                'priority_score': card.get('edhrecPriorityScore', 0),
                'priority_level': card.get('edhrecPriorityLevel', 'minimal'),
                'priority_tier': card.get('edhrecPriorityTier', 'unranked'),
                'reasons': card.get('edhrecPriorityReasons', []),
                'type': card.get('type', 'Unknown'),
                'rarity': card.get('rarity', 'unknown'),
                'has_relationships': len(card.get('allParts', [])) > 0,
                'relationship_count': len(card.get('allParts', []))
            })
        
        return results
    
    def analyze_edhrec_coverage(self) -> Dict[str, any]:
        """Analyze how much of the database has EDHREC coverage."""
        total_cards = self.cards_collection.count_documents({})
        
        with_edhrec = self.cards_collection.count_documents({
            'edhrecRank': {'$exists': True, '$type': 'number'}
        })
        
        analyzed_with_edhrec = self.cards_collection.count_documents({
            '$and': [
                {'analysis': {'$exists': True, '$ne': ''}},
                {'edhrecRank': {'$exists': True, '$type': 'number'}}
            ]
        })
        
        unanalyzed_with_edhrec = self.cards_collection.count_documents({
            '$and': [
                {'analysis': {'$exists': False}},
                {'edhrecRank': {'$exists': True, '$type': 'number'}}
            ]
        })
        
        # Get tier distribution
        tier_distribution = {}
        for tier_name, tier_info in self.priority_tiers.items():
            count = self.cards_collection.count_documents({
                '$and': [
                    {'edhrecRank': {'$gte': tier_info['min_rank'], '$lte': tier_info['max_rank']}},
                    {'analysis': {'$exists': False}}
                ]
            })
            tier_distribution[tier_name] = count
        
        return {
            'total_cards': total_cards,
            'cards_with_edhrec': with_edhrec,
            'edhrec_coverage_percent': round((with_edhrec / total_cards) * 100, 1),
            'analyzed_with_edhrec': analyzed_with_edhrec,
            'unanalyzed_with_edhrec': unanalyzed_with_edhrec,
            'unanalyzed_tier_distribution': tier_distribution
        }

def main():
    """Demonstrate EDHREC-based prioritization."""
    manager = EDHRECPriorityManager()
    
    print("🏆 EDHREC-BASED ANALYSIS PRIORITIZATION")
    print("=" * 50)
    
    # Analyze current EDHREC coverage
    coverage = manager.analyze_edhrec_coverage()
    print(f"\n📊 EDHREC COVERAGE ANALYSIS:")
    print(f"  Total cards in database: {coverage['total_cards']:,}")
    print(f"  Cards with EDHREC rankings: {coverage['cards_with_edhrec']:,} ({coverage['edhrec_coverage_percent']}%)")
    print(f"  Analyzed cards with EDHREC: {coverage['analyzed_with_edhrec']:,}")
    print(f"  Unanalyzed cards with EDHREC: {coverage['unanalyzed_with_edhrec']:,}")
    
    print(f"\n🎯 UNANALYZED CARDS BY EDHREC TIER:")
    for tier, count in coverage['unanalyzed_tier_distribution'].items():
        if count > 0:
            tier_info = manager.priority_tiers[tier]
            print(f"  {tier.title()}: {count} cards (ranks {tier_info['min_rank']}-{tier_info['max_rank']})")
    
    # Update priorities
    print(f"\n🔄 Updating EDHREC priorities...")
    results = manager.update_all_edhrec_priorities()
    print(f"✅ Updated {results['updated_count']} cards")
    print(f"   Priority levels: {results['priority_distribution']}")
    print(f"   Score ranges: {results['score_ranges']}")
    
    # Show top priority queue
    print(f"\n🚀 TOP EDHREC PRIORITY QUEUE:")
    queue = manager.get_edhrec_priority_queue(15)
    
    for i, card in enumerate(queue, 1):
        print(f"\n{i:2d}. {card['name']} (EDHREC #{card['edhrec_rank']})")
        print(f"    Score: {card['priority_score']} | Tier: {card['priority_tier']} | Level: {card['priority_level']}")
        print(f"    Type: {card['type']} | Rarity: {card['rarity'].title()}")
        if card['has_relationships']:
            print(f"    🔗 {card['relationship_count']} card relationships")
        print(f"    Reasons: {'; '.join(card['reasons'][:2])}")
    
    if not queue:
        print("   No cards found with EDHREC priorities. Run Scryfall import first!")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"   Use this EDHREC-based queue instead of random selection!")
    print(f"   Top-tier cards (legendary/critical) should be prioritized for analysis.")

if __name__ == "__main__":
    main()
