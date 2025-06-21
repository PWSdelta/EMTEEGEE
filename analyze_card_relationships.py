#!/usr/bin/env python3
"""
Card Relationship Graph Analyzer for EMTEEGEE
Analyzes card relationships from Scryfall's all_parts data to prioritize analysis requests.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import networkx as nx

# Add the project root to sys.path for Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
import django
django.setup()

from cards.models import get_cards_collection

class CardRelationshipAnalyzer:
    """Analyzes card relationships to build priority graphs and suggest analysis targets."""
    
    def __init__(self):
        self.cards_collection = get_cards_collection()
        self.relationship_graph = nx.DiGraph()
        self.relationship_types = {
            'token': 'creates/is token',
            'meld_part': 'melds with',
            'meld_result': 'result of meld',
            'combo_piece': 'part of combo'
        }
    
    def build_relationship_graph(self) -> Dict[str, any]:
        """Build a graph of card relationships from the database."""
        print("🔍 Building card relationship graph...")
        
        # Get all cards with relationship data
        cards_with_relations = list(self.cards_collection.find({
            'allParts': {'$exists': True, '$ne': []}
        }, {
            'name': 1, 'allParts': 1, 'scryfallId': 1, 'analysis': 1,
            'analysisRequested': 1, 'edhrecRank': 1, 'rarity': 1
        }))
        
        relationship_stats = {
            'total_cards_with_relations': len(cards_with_relations),
            'relationship_types': Counter(),
            'connected_components': 0,
            'most_connected_cards': [],
            'priority_suggestions': []
        }
        
        # Build the graph
        for card in cards_with_relations:
            card_name = card['name']
            self.relationship_graph.add_node(card_name, **card)
            
            # Add edges for each related card
            for related_part in card.get('allParts', []):
                related_name = related_part.get('name')
                component_type = related_part.get('component', 'related')
                
                if related_name and related_name != card_name:
                    self.relationship_graph.add_edge(
                        card_name, related_name,
                        relationship=component_type,
                        type=self.relationship_types.get(component_type, component_type)
                    )
                    relationship_stats['relationship_types'][component_type] += 1
        
        # Analyze the graph
        relationship_stats['connected_components'] = nx.number_weakly_connected_components(self.relationship_graph)
        
        # Find most connected cards
        node_degrees = dict(self.relationship_graph.degree())
        most_connected = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        relationship_stats['most_connected_cards'] = most_connected
        
        # Generate priority suggestions
        relationship_stats['priority_suggestions'] = self._generate_priority_suggestions()
        
        print(f"✅ Graph built: {len(self.relationship_graph.nodes)} cards, {len(self.relationship_graph.edges)} relationships")
        return relationship_stats
    
    def _generate_priority_suggestions(self) -> List[Dict[str, any]]:
        """Generate analysis priority suggestions based on relationships."""
        suggestions = []
        
        # Strategy 1: High-degree nodes without analysis
        for card_name, degree in sorted(dict(self.relationship_graph.degree()).items(), 
                                       key=lambda x: x[1], reverse=True)[:20]:
            card_data = self.relationship_graph.nodes[card_name]
            
            if not card_data.get('analysis') and not card_data.get('analysisRequested'):
                suggestions.append({
                    'card_name': card_name,
                    'strategy': 'high_connectivity',
                    'priority_score': degree * 10,  # Base score on connections
                    'reason': f'Hub card with {degree} relationships - analyzing this could unlock {degree} related cards',
                    'connected_cards': list(self.relationship_graph.neighbors(card_name)),
                    'edhrec_rank': card_data.get('edhrecRank'),
                    'rarity': card_data.get('rarity')
                })
        
        # Strategy 2: Complete connected components
        for component in nx.weakly_connected_components(self.relationship_graph):
            if len(component) >= 3:  # Only consider components with 3+ cards
                analyzed_count = sum(1 for card in component 
                                   if self.relationship_graph.nodes[card].get('analysis'))
                unanalyzed = [card for card in component 
                            if not self.relationship_graph.nodes[card].get('analysis') 
                            and not self.relationship_graph.nodes[card].get('analysisRequested')]
                
                if analyzed_count > 0 and unanalyzed:  # Some analyzed, some not
                    for card_name in unanalyzed[:2]:  # Top 2 from this component
                        card_data = self.relationship_graph.nodes[card_name]
                        suggestions.append({
                            'card_name': card_name,
                            'strategy': 'complete_component',
                            'priority_score': len(component) * 5 + analyzed_count * 2,
                            'reason': f'Part of {len(component)}-card relationship cluster, {analyzed_count} already analyzed',
                            'component_size': len(component),
                            'analyzed_in_component': analyzed_count,
                            'edhrec_rank': card_data.get('edhrecRank'),
                            'rarity': card_data.get('rarity')
                        })
        
        # Strategy 3: Popular cards with relationships
        popular_unanalyzed = []
        for card_name in self.relationship_graph.nodes:
            card_data = self.relationship_graph.nodes[card_name]
            edhrec_rank = card_data.get('edhrecRank')
            
            if (edhrec_rank and edhrec_rank <= 1000 and  # Top 1000 on EDHREC
                not card_data.get('analysis') and 
                not card_data.get('analysisRequested')):
                
                degree = self.relationship_graph.degree[card_name]
                if degree > 0:  # Has relationships
                    popular_unanalyzed.append({
                        'card_name': card_name,
                        'strategy': 'popular_with_relations',
                        'priority_score': (1001 - edhrec_rank) // 10 + degree,
                        'reason': f'EDHREC rank #{edhrec_rank} with {degree} relationships',
                        'edhrec_rank': edhrec_rank,
                        'relationship_count': degree,
                        'rarity': card_data.get('rarity')
                    })
        
        suggestions.extend(sorted(popular_unanalyzed, key=lambda x: x['priority_score'], reverse=True)[:10])
        
        # Sort all suggestions by priority score
        suggestions.sort(key=lambda x: x['priority_score'], reverse=True)
        return suggestions[:25]  # Top 25 suggestions
    
    def get_relationship_chain(self, start_card: str, max_depth: int = 3) -> List[List[str]]:
        """Get chains of related cards starting from a given card."""
        if start_card not in self.relationship_graph:
            return []
        
        chains = []
        visited = set()
        
        def dfs_chains(current_card: str, current_chain: List[str], depth: int):
            if depth >= max_depth or current_card in visited:
                return
            
            visited.add(current_card)
            current_chain.append(current_card)
            
            neighbors = list(self.relationship_graph.neighbors(current_card))
            if not neighbors:
                if len(current_chain) > 1:
                    chains.append(current_chain.copy())
            else:
                for neighbor in neighbors:
                    dfs_chains(neighbor, current_chain.copy(), depth + 1)
        
        dfs_chains(start_card, [], 0)
        return chains
    
    def analyze_card_importance(self, card_name: str) -> Dict[str, any]:
        """Analyze the importance/centrality of a specific card in the relationship graph."""
        if card_name not in self.relationship_graph:
            return {'error': f'Card "{card_name}" not found in relationship graph'}
        
        # Calculate various centrality measures
        try:
            betweenness = nx.betweenness_centrality(self.relationship_graph.to_undirected()).get(card_name, 0)
            closeness = nx.closeness_centrality(self.relationship_graph.to_undirected()).get(card_name, 0)
            pagerank = nx.pagerank(self.relationship_graph).get(card_name, 0)
        except:
            betweenness = closeness = pagerank = 0
        
        degree = self.relationship_graph.degree[card_name]
        neighbors = list(self.relationship_graph.neighbors(card_name))
        
        # Get relationship types
        relationship_breakdown = Counter()
        for neighbor in neighbors:
            edge_data = self.relationship_graph.get_edge_data(card_name, neighbor)
            rel_type = edge_data.get('relationship', 'unknown') if edge_data else 'unknown'
            relationship_breakdown[rel_type] += 1
        
        return {
            'card_name': card_name,
            'degree': degree,
            'connected_cards': neighbors,
            'relationship_types': dict(relationship_breakdown),
            'centrality_scores': {
                'betweenness': betweenness,
                'closeness': closeness,
                'pagerank': pagerank
            },
            'importance_score': degree * 2 + betweenness * 100 + pagerank * 50,
            'chains_from_card': self.get_relationship_chain(card_name)
        }

def main():
    """Analyze card relationships and generate priority suggestions."""
    analyzer = CardRelationshipAnalyzer()
    
    print("🕸️ CARD RELATIONSHIP ANALYSIS")
    print("=" * 50)
    
    # Build the relationship graph
    stats = analyzer.build_relationship_graph()
    
    print(f"\n📊 RELATIONSHIP STATISTICS:")
    print(f"  - Cards with relationships: {stats['total_cards_with_relations']}")
    print(f"  - Connected components: {stats['connected_components']}")
    print(f"  - Relationship types: {dict(stats['relationship_types'])}")
    
    print(f"\n🔗 MOST CONNECTED CARDS:")
    for card_name, degree in stats['most_connected_cards'][:5]:
        print(f"  - {card_name}: {degree} connections")
    
    print(f"\n🎯 TOP PRIORITY SUGGESTIONS:")
    for i, suggestion in enumerate(stats['priority_suggestions'][:10], 1):
        print(f"  {i}. {suggestion['card_name']} (Score: {suggestion['priority_score']})")
        print(f"     Strategy: {suggestion['strategy']}")
        print(f"     Reason: {suggestion['reason']}")
        if suggestion.get('edhrec_rank'):
            print(f"     EDHREC Rank: #{suggestion['edhrec_rank']}")
        print()
    
    # Analyze a specific high-priority card
    if stats['priority_suggestions']:
        top_card = stats['priority_suggestions'][0]['card_name']
        print(f"🔍 DETAILED ANALYSIS: {top_card}")
        analysis = analyzer.analyze_card_importance(top_card)
        print(f"  - Connections: {analysis['degree']}")
        print(f"  - Relationship types: {analysis['relationship_types']}")
        print(f"  - Importance score: {analysis['importance_score']:.2f}")
        if analysis.get('chains_from_card'):
            print(f"  - Example relationship chain: {' -> '.join(analysis['chains_from_card'][0])}")

if __name__ == "__main__":
    main()
