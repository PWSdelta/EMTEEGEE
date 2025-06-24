#!/usr/bin/env python3
"""
EMTEEGEE Synthesis Manager
========================
Synthesizes all component analyses into a single, cohesive "complete_analysis" field.
This creates a unified, user-friendly analysis that combines insights from all 20 components.

Beast laptop will generate these synthesis reports after all components are complete.
"""

import os
import sys
import socket
import logging
import ollama
from datetime import datetime
from typing import Dict, Any, Optional, List

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')

import django
django.setup()

from cards.models import get_cards_collection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SYNTHESIS - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SynthesisManager:
    """Manages synthesis of component analyses into complete analyses."""
    
    def __init__(self):
        self.cards_collection = get_cards_collection()
        self.hostname = socket.gethostname().lower()
        self.is_beast_laptop = 'beast' in self.hostname
          # Initialize Ollama client with the beast laptop's model
        if self.is_beast_laptop:
            self.model = "llama3.3:70b"
        else:
            # Fallback models for other machines
            if 'desktop' in self.hostname:
                self.model = "llama3.1:8b"
            else:
                self.model = "llama3.2:3b"
                
        logger.info(f"Synthesis Manager initialized on {self.hostname} with model {self.model}")
    
    def should_synthesize_on_this_machine(self) -> bool:
        """Only the beast laptop should generate synthesis reports."""
        return self.is_beast_laptop
    
    def find_cards_ready_for_synthesis(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find cards that have all 20 components but no complete_analysis yet."""
        pipeline = [
            {
                '$match': {
                    'analysis.components': {'$exists': True},
                    'analysis.complete_analysis': {'$exists': False}  # No synthesis yet
                }
            },
            {
                '$addFields': {
                    'component_count': {
                        '$cond': {
                            'if': {'$eq': [{'$type': '$analysis.components'}, 'object']},
                            'then': {'$size': {'$objectToArray': '$analysis.components'}},
                            'else': 0
                        }
                    }
                }
            },
            {
                '$match': {
                    'component_count': {'$eq': 20}  # All components complete
                }
            },
            {
                '$sort': {
                    'edhrecRank': 1  # Prioritize popular cards
                }
            },
            {'$limit': limit}
        ]
        
        return list(self.cards_collection.aggregate(pipeline))
    
    def extract_component_insights(self, components: Dict[str, Any]) -> Dict[str, str]:
        """Extract key insights from each component category."""
        insights = {
            'strategic': [],
            'practical': [],
            'educational': [],
            'thematic': []
        }
        
        # Component categorization (matches the frontend)
        component_categories = {
            'strategic': [
                'tactical_analysis', 'power_level_assessment', 'meta_position', 
                'competitive_viability', 'deckbuilding_analysis'
            ],
            'practical': [
                'play_tips', 'combo_suggestions', 'synergy_analysis', 
                'optimization_suggestions', 'budget_considerations'
            ],
            'educational': [
                'new_player_guide', 'rules_clarifications', 'format_analysis', 
                'historical_significance', 'design_philosophy'
            ],
            'thematic': [
                'thematic_analysis', 'art_flavor_analysis', 'lore_connections', 
                'creative_inspiration', 'community_perception'
            ]
        }
        
        for category, component_types in component_categories.items():
            for comp_type in component_types:
                if comp_type in components:
                    comp_data = components[comp_type]
                    content = comp_data.get('content', '') if isinstance(comp_data, dict) else str(comp_data)
                    if content.strip():
                        # Extract the first meaningful sentence or key point
                        first_sentence = content.split('.')[0].strip()
                        if len(first_sentence) > 20:  # Meaningful content
                            insights[category].append(first_sentence)
        
        return insights
    
    def generate_synthesis_prompt(self, card: Dict[str, Any], insights: Dict[str, str]) -> str:
        """Generate the prompt for synthesizing the complete analysis."""
        name = card.get('name', 'Unknown Card')
        card_type = card.get('type', '')
        mana_cost = card.get('manaCost', '')
        
        prompt = f"""You are an expert Magic: The Gathering analyst creating a comprehensive analysis summary.

CARD: {name}
TYPE: {card_type}
MANA COST: {mana_cost}

You have access to detailed analysis from 20 different components. Your task is to synthesize this into ONE cohesive, user-friendly analysis that captures the most important insights.

COMPONENT INSIGHTS BY CATEGORY:

STRATEGIC INSIGHTS:
{chr(10).join(f"• {insight}" for insight in insights['strategic'][:5])}

PRACTICAL INSIGHTS:
{chr(10).join(f"• {insight}" for insight in insights['practical'][:5])}

EDUCATIONAL INSIGHTS:
{chr(10).join(f"• {insight}" for insight in insights['educational'][:3])}

THEMATIC INSIGHTS:
{chr(10).join(f"• {insight}" for insight in insights['thematic'][:3])}

Create a COMPLETE ANALYSIS that:
1. Starts with a clear, engaging overview of what this card does and why it matters
2. Covers the most important strategic and competitive aspects
3. Includes practical deckbuilding and play advice
4. Mentions key synergies, combos, or optimization tips
5. Provides context about its place in Magic's history/meta
6. Is written in an engaging, accessible style for both new and experienced players

Length: 300-500 words
Tone: Informative but engaging, like a knowledgeable friend explaining the card
Format: Well-structured paragraphs, not bullet points

COMPLETE ANALYSIS:"""

        return prompt
    
    def generate_complete_analysis(self, card: Dict[str, Any]) -> Optional[str]:
        """Generate a complete analysis by synthesizing all components."""
        try:
            name = card.get('name', 'Unknown Card')
            logger.info(f"Generating synthesis for {name}")
            
            components = card.get('analysis', {}).get('components', {})
            if len(components) < 20:
                logger.warning(f"Card {name} only has {len(components)} components, skipping synthesis")
                return None
            
            # Extract insights from components
            insights = self.extract_component_insights(components)
            
            # Generate synthesis prompt
            prompt = self.generate_synthesis_prompt(card, insights)
              # Use Ollama to generate the synthesis
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': 'You are an expert Magic: The Gathering analyst creating comprehensive analysis summaries.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            if response and 'message' in response and 'content' in response['message']:
                content = response['message']['content'].strip()
                if len(content) > 100:
                    logger.info(f"Successfully generated synthesis for {name} ({len(content)} characters)")
                    return content
                else:
                    logger.error(f"Generated synthesis too short for {name}")
                    return None
            else:
                logger.error(f"Invalid response from Ollama for {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating synthesis for {card.get('name', 'Unknown')}: {e}")
            return None
    
    def save_complete_analysis(self, card_uuid: str, complete_analysis: str) -> bool:
        """Save the complete analysis to the database."""
        try:
            result = self.cards_collection.update_one(
                {'uuid': card_uuid},
                {                    '$set': {
                        'analysis.complete_analysis': complete_analysis,
                        'analysis.synthesis_generated_at': datetime.now(),
                        'analysis.synthesis_generated_by': f"{self.hostname}-{self.model}",
                        'analysis.synthesis_version': 1.0
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Saved complete analysis for card {card_uuid}")
                return True
            else:
                logger.warning(f"No document updated for card {card_uuid}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving complete analysis for {card_uuid}: {e}")
            return False
    
    def run_synthesis_batch(self, batch_size: int = 5) -> Dict[str, int]:
        """Run a batch of synthesis operations."""
        if not self.should_synthesize_on_this_machine():
            logger.info(f"Synthesis skipped - this machine ({self.hostname}) is not the beast laptop")
            return {'skipped': 1, 'reason': 'not_beast_laptop'}
        
        logger.info(f"Starting synthesis batch (size: {batch_size})")
        
        # Find cards ready for synthesis
        cards_ready = self.find_cards_ready_for_synthesis(batch_size)
        
        if not cards_ready:
            logger.info("No cards ready for synthesis")
            return {'processed': 0, 'success': 0, 'failed': 0}
        
        results = {'processed': 0, 'success': 0, 'failed': 0}
        
        for card in cards_ready:
            try:
                name = card.get('name', 'Unknown')
                uuid = card.get('uuid')
                
                if not uuid:
                    logger.error(f"Card {name} has no UUID, skipping")
                    results['failed'] += 1
                    continue
                
                logger.info(f"Processing synthesis for {name}")
                results['processed'] += 1
                
                # Generate the complete analysis
                complete_analysis = self.generate_complete_analysis(card)
                
                if complete_analysis:
                    # Save to database
                    if self.save_complete_analysis(uuid, complete_analysis):
                        results['success'] += 1
                        logger.info(f"✓ Synthesis complete for {name}")
                    else:
                        results['failed'] += 1
                        logger.error(f"✗ Failed to save synthesis for {name}")
                else:
                    results['failed'] += 1
                    logger.error(f"✗ Failed to generate synthesis for {name}")
            
            except Exception as e:
                logger.error(f"Error processing synthesis for {card.get('name', 'Unknown')}: {e}")
                results['failed'] += 1
        
        logger.info(f"Synthesis batch complete: {results}")
        return results
    
    def get_synthesis_stats(self) -> Dict[str, int]:
        """Get statistics about synthesis progress."""
        try:
            # Total cards with all 20 components
            cards_with_all_components = self.cards_collection.count_documents({
                '$expr': {
                    '$eq': [
                        {'$size': {'$objectToArray': '$analysis.components'}},
                        20
                    ]
                }
            })
            
            # Cards with complete analysis
            cards_with_synthesis = self.cards_collection.count_documents({
                'analysis.complete_analysis': {'$exists': True}
            })
            
            # Cards ready for synthesis
            cards_ready_for_synthesis = cards_with_all_components - cards_with_synthesis
            
            return {
                'cards_with_all_components': cards_with_all_components,
                'cards_with_synthesis': cards_with_synthesis,
                'cards_ready_for_synthesis': cards_ready_for_synthesis,
                'synthesis_completion_rate': round((cards_with_synthesis / max(cards_with_all_components, 1)) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting synthesis stats: {e}")
            return {
                'cards_with_all_components': 0,
                'cards_with_synthesis': 0,
                'cards_ready_for_synthesis': 0,
                'synthesis_completion_rate': 0.0
            }

# Global instance
synthesis_manager = SynthesisManager()

def main():
    """Run synthesis as a standalone script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='EMTEEGEE Synthesis Manager')
    parser.add_argument('--batch-size', type=int, default=5, help='Number of cards to process in batch')
    parser.add_argument('--stats', action='store_true', help='Show synthesis statistics')
    
    args = parser.parse_args()
    
    if args.stats:
        stats = synthesis_manager.get_synthesis_stats()
        logger.info("Synthesis Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
    else:
        results = synthesis_manager.run_synthesis_batch(args.batch_size)
        logger.info(f"Batch processing complete: {results}")

if __name__ == '__main__':
    main()
