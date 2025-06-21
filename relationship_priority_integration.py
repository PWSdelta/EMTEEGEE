#!/usr/bin/env python3
"""
Integration script for card relationship-based analysis prioritization.
Integrates with existing analysis request system to prioritize based on card relationships.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, List
from collections import Counter
from pymongo import UpdateOne

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

class RelationshipPriorityIntegrator:
    """Integrates card relationships with the existing analysis request system."""
    
    def __init__(self):
        self.cards_collection = get_cards_collection()
    
    def get_relationship_priority_score(self, card_name: str) -> int:
        """Calculate priority score based on card relationships."""
        card = self.cards_collection.find_one({'name': card_name})
        if not card:
            return 0
        
        base_score = 0
        
        # Score based on relationships
        all_parts = card.get('allParts', [])
        relationship_count = len(all_parts)
        base_score += relationship_count * 10  # 10 points per relationship
        
        # Bonus for different relationship types
        relationship_types = set(part.get('component', 'related') for part in all_parts)
        base_score += len(relationship_types) * 5  # 5 points per unique relationship type
        
        # EDHREC popularity bonus
        edhrec_rank = card.get('edhrecRank')
        if edhrec_rank:
            if edhrec_rank <= 100:
                base_score += 50  # Top 100
            elif edhrec_rank <= 500:
                base_score += 25  # Top 500
            elif edhrec_rank <= 1000:
                base_score += 10  # Top 1000
        
        # Rarity bonus (rare/mythic cards are often more impactful)
        rarity = card.get('rarity', '').lower()
        if rarity == 'mythic':
            base_score += 15
        elif rarity == 'rare':
            base_score += 10
        
        # Bonus if related cards already have analysis (completion incentive)
        analyzed_related_count = 0
        for part in all_parts:
            related_card = self.cards_collection.find_one({
                'name': part.get('name'),
                'analysis': {'$exists': True, '$ne': ''}
            })
            if related_card:
                analyzed_related_count += 1
        
        if analyzed_related_count > 0:
            base_score += analyzed_related_count * 8  # 8 points per analyzed related card
        
        return base_score
    
    def get_relationship_context(self, card_name: str) -> Dict[str, any]:
        """Get relationship context for a card to inform analysis."""
        card = self.cards_collection.find_one({'name': card_name})
        if not card:
            return {}
        
        context = {
            'has_relationships': False,
            'relationship_summary': '',
            'related_cards': [],
            'analysis_suggestions': []
        }
        
        all_parts = card.get('allParts', [])
        if not all_parts:
            return context
        
        context['has_relationships'] = True
        
        # Categorize relationships
        relationship_breakdown = Counter()
        related_cards_info = []
        
        for part in all_parts:
            part_name = part.get('name')
            component_type = part.get('component', 'related')
            relationship_breakdown[component_type] += 1
            
            # Get info about the related card
            related_card = self.cards_collection.find_one({'name': part_name})
            related_info = {
                'name': part_name,
                'component': component_type,
                'has_analysis': bool(related_card and related_card.get('analysis')) if related_card else False,
                'type_line': related_card.get('type') if related_card else part.get('type_line', 'Unknown')
            }
            related_cards_info.append(related_info)
        
        context['related_cards'] = related_cards_info
        
        # Create summary
        summary_parts = []
        for rel_type, count in relationship_breakdown.items():
            type_name = {
                'token': 'creates/is token',
                'meld_part': 'melds with other cards',
                'meld_result': 'result of melding',
                'combo_piece': 'part of combo'
            }.get(rel_type, rel_type)
            summary_parts.append(f"{count} {type_name}")
        
        context['relationship_summary'] = f"This card has relationships: {', '.join(summary_parts)}"
        
        # Generate analysis suggestions
        suggestions = []
        
        # Suggest analyzing related cards that don't have analysis
        unanalyzed_related = [card for card in related_cards_info if not card['has_analysis']]
        if unanalyzed_related:
            suggestions.append(f"Consider analyzing related cards: {', '.join([card['name'] for card in unanalyzed_related[:3]])}")
          # Suggest relationship-specific analysis points
        if 'token' in relationship_breakdown:
            suggestions.append("Focus on token generation and synergies in analysis")
        if 'meld_part' in relationship_breakdown or 'meld_result' in relationship_breakdown:
            suggestions.append("Discuss meld mechanics and the combined card's power level")
        if 'combo_piece' in relationship_breakdown:
            suggestions.append("Explore combo potential and interaction with related cards")
        
        context['analysis_suggestions'] = suggestions
        
        return context
    
    def update_analysis_priorities(self) -> Dict[str, int]:
        """Update analysis priorities for all cards based on relationships using bulk operations."""
        print("🔄 Updating analysis priorities based on relationships...")
        
        # Get all cards that need analysis but don't have it
        unanalyzed_cards = list(self.cards_collection.find({
            '$and': [
                {'analysis': {'$exists': False}},
                {'analysisRequested': {'$ne': True}}
            ]
        }, {'name': 1}))
        
        print(f"Found {len(unanalyzed_cards)} unanalyzed cards to process")
        
        updated_count = 0
        priority_distribution = Counter()
        batch_size = 2357
        
        # Process cards in batches for optimal performance
        for i in range(0, len(unanalyzed_cards), batch_size):
            batch = unanalyzed_cards[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(unanalyzed_cards) + batch_size - 1) // batch_size
            
            print(f"Processing relationship priority batch {batch_num}/{total_batches} ({len(batch)} cards)")
            
            # Prepare bulk operations for this batch
            bulk_operations = []
            
            for card_doc in batch:
                card_name = card_doc['name']
                priority_score = self.get_relationship_priority_score(card_name)
                
                if priority_score > 0:  # Only update if there's a meaningful priority
                    # Map score to priority levels
                    if priority_score >= 50:
                        priority = 'high'
                    elif priority_score >= 25:
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    # Prepare bulk update operation
                    bulk_operations.append(
                        UpdateOne(
                            {'name': card_name},
                            {
                                '$set': {
                                    'relationshipPriorityScore': priority_score,
                                    'relationshipPriority': priority,
                                    'priorityUpdatedAt': datetime.now(timezone.utc).isoformat()
                                }
                            }
                        )
                    )
                    updated_count += 1
                    priority_distribution[priority] += 1
            
            # Execute bulk operations for this batch
            if bulk_operations:
                try:
                    print(f"Executing {len(bulk_operations)} relationship priority updates for batch {batch_num}")
                    result = self.cards_collection.bulk_write(bulk_operations, ordered=False)
                    print(f"Batch {batch_num} completed: {result.modified_count} cards updated")
                except Exception as e:
                    print(f"Error in batch {batch_num}: {e}")
                    # Adjust count if batch failed
                    failed_ops = len(bulk_operations)
                    updated_count -= failed_ops
                    for op in bulk_operations:
                        # Remove from priority distribution count
                        priority = 'high' if op._doc['$set']['relationshipPriorityScore'] >= 50 else \
                                  'medium' if op._doc['$set']['relationshipPriorityScore'] >= 25 else 'low'
                        priority_distribution[priority] -= 1
        
        print(f"✅ Updated {updated_count} cards with relationship priorities")
        print(f"   Priority distribution: {dict(priority_distribution)}")
        
        return {
            'updated_count': updated_count,
            'priority_distribution': dict(priority_distribution)
        }
    
    def get_next_priority_cards(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get the next highest priority cards for analysis based on relationships."""
        priority_cards = list(self.cards_collection.find({
            '$and': [
                {'analysis': {'$exists': False}},
                {'analysisRequested': {'$ne': True}},
                {'relationshipPriorityScore': {'$exists': True}}
            ]
        }).sort('relationshipPriorityScore', -1).limit(limit))
        
        results = []
        for card in priority_cards:
            context = self.get_relationship_context(card['name'])
            results.append({
                'name': card['name'],
                'priority_score': card.get('relationshipPriorityScore', 0),
                'priority_level': card.get('relationshipPriority', 'low'),
                'relationship_summary': context.get('relationship_summary', ''),
                'related_cards_count': len(context.get('related_cards', [])),
                'analysis_suggestions': context.get('analysis_suggestions', [])
            })
        
        return results

def main():
    """Update priorities and show top relationship-based candidates."""
    integrator = RelationshipPriorityIntegrator()
    
    print("🕸️ RELATIONSHIP-BASED ANALYSIS PRIORITIZATION")
    print("=" * 55)
    
    # Update all priorities
    results = integrator.update_analysis_priorities()
    
    # Show top candidates
    print("\n🎯 TOP RELATIONSHIP-PRIORITY CARDS FOR ANALYSIS:")
    top_cards = integrator.get_next_priority_cards(10)
    
    for i, card_info in enumerate(top_cards, 1):
        print(f"\n{i}. {card_info['name']} (Score: {card_info['priority_score']}, Priority: {card_info['priority_level']})")
        print(f"   {card_info['relationship_summary']}")
        if card_info.get('analysis_suggestions'):
            print(f"   💡 Suggestions: {'; '.join(card_info['analysis_suggestions'][:2])}")
    
    if not top_cards:
        print("   No cards found with relationship priorities. Run Scryfall import first!")

if __name__ == "__main__":
    main()
