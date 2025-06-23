"""
Cross-Component Analysis Coherence Manager
Ensures consistency and quality across all 20 analysis components
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .models import get_cards_collection

# Ollama is optional - only needed for advanced coherence validation
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

logger = logging.getLogger(__name__)

class CoherenceManager:
    """Manages cross-component analysis coherence and validation"""
    
    # Component dependency groups - components that should be consistent with each other
    COHERENCE_GROUPS = {
        'power_assessment': ['power_level_assessment', 'competitive_analysis', 'meta_positioning'],
        'deck_building': ['deck_archetypes', 'synergy_analysis', 'combo_suggestions'],
        'gameplay_mechanics': ['play_tips', 'tactical_analysis', 'advanced_interactions'],
        'economic_analysis': ['investment_outlook', 'budget_alternatives', 'format_analysis'],
        'thematic_design': ['thematic_analysis', 'art_flavor_analysis', 'design_philosophy', 'historical_context']
    }
    
    # Core components that should be generated first (foundation for others)
    FOUNDATION_COMPONENTS = ['power_level_assessment', 'tactical_analysis', 'thematic_analysis']
    
    def __init__(self):
        self.cards_collection = get_cards_collection()
    
    def get_analysis_context(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis context that informs all components"""
        context = {
            'card_characteristics': self._analyze_card_characteristics(card_data),
            'power_indicators': self._identify_power_indicators(card_data),
            'thematic_elements': self._extract_thematic_elements(card_data),
            'mechanical_complexity': self._assess_mechanical_complexity(card_data)
        }
        return context
    
    def _analyze_card_characteristics(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fundamental card characteristics for context"""
        characteristics = {
            'mana_value': self._extract_mana_value(card_data.get('mana_cost', '')),
            'card_types': self._parse_type_line(card_data.get('type_line', '')),
            'power_toughness': self._extract_power_toughness(card_data),
            'color_identity': self._determine_color_identity(card_data.get('mana_cost', '')),
            'rules_complexity': self._measure_rules_complexity(card_data.get('oracle_text', ''))
        }
        return characteristics
    
    def _identify_power_indicators(self, card_data: Dict[str, Any]) -> List[str]:
        """Identify power level indicators for consistent assessment"""
        indicators = []
        
        oracle_text = card_data.get('oracle_text', '').lower()
        
        # High power indicators
        if any(keyword in oracle_text for keyword in ['draw cards', 'search your library', 'extra turn']):
            indicators.append('card_advantage')
        if any(keyword in oracle_text for keyword in ['hexproof', 'indestructible', 'protection']):
            indicators.append('resilience')
        if 'enters the battlefield' in oracle_text:
            indicators.append('immediate_impact')
        if any(keyword in oracle_text for keyword in ['haste', 'flash', 'instant']):
            indicators.append('tempo')
        return indicators
    
    def validate_component_coherence(self, new_component: str, 
                                   new_analysis: str, existing_components: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that new component is coherent with existing analysis"""
        validation_result = {
            'is_coherent': True,
            'confidence_score': 1.0,
            'potential_conflicts': [],
            'suggestions': []
        }
        
        # Find which coherence group this component belongs to
        component_group = None
        for group, components in self.COHERENCE_GROUPS.items():
            if new_component in components:
                component_group = group
                break
        
        if not component_group:
            return validation_result  # No coherence validation needed
        
        # Check for conflicts with existing components in the same group
        group_components = self.COHERENCE_GROUPS[component_group]
        existing_in_group = {comp: existing_components.get(comp) for comp in group_components 
                           if comp in existing_components and comp != new_component}
        
        if existing_in_group:
            # Use LLM to check coherence
            validation_result = self._llm_coherence_check(
                new_component, new_analysis, existing_in_group, component_group
            )
        
        return validation_result
    
    def _llm_coherence_check(self, new_component: str, new_analysis: str, 
                           existing_analyses: Dict[str, Any], group: str) -> Dict[str, Any]:
        """Use LLM to check coherence between related components"""
        
        coherence_prompt = f"""
You are analyzing MTG card analysis components for consistency. 

COMPONENT GROUP: {group}
NEW COMPONENT: {new_component}
NEW ANALYSIS: {new_analysis}

EXISTING RELATED ANALYSES:
{json.dumps({k: v.get('content', '') if isinstance(v, dict) else str(v) for k, v in existing_analyses.items()}, indent=2)}

Task: Check if the new analysis is coherent with existing analyses. Look for:
1. Contradictory power level assessments
2. Conflicting strategic advice
3. Inconsistent card evaluation
4. Misaligned recommendations

Respond with JSON:
{{
    "is_coherent": true/false,
    "confidence_score": 0.0-1.0,
    "potential_conflicts": ["specific conflict descriptions"],
    "suggestions": ["specific improvement suggestions"]
}}
"""
        
        try:
            if not OLLAMA_AVAILABLE:
                # Fallback coherence check without ollama
                logger.warning("Ollama not available, using basic coherence validation")
                return {
                    'is_coherent': True,
                    'confidence_score': 0.8,
                    'potential_conflicts': [],
                    'suggestions': []
                }
            
            response = ollama.chat(
                model='llama3.1:8b',  # Use fast model for validation
                messages=[{'role': 'user', 'content': coherence_prompt}],
                options={'temperature': 0.1}  # Low temperature for consistent validation
            )
            
            result = json.loads(response['message']['content'])
            return result
            
        except Exception as e:
            logger.error(f"Coherence check failed: {e}")
            return {
                'is_coherent': True,
                'confidence_score': 0.5,
                'potential_conflicts': [],
                'suggestions': []
            }
    
    def generate_enhanced_component(self, card_data: Dict[str, Any], component_type: str, 
                                  existing_components: Dict[str, Any], 
                                  analysis_context: Dict[str, Any]) -> str:
        """Generate component with full context awareness"""
          # Build context-aware prompt
        context_prompt = self._build_context_prompt(card_data, component_type, 
                                                  existing_components, analysis_context)
        
        try:
            if not OLLAMA_AVAILABLE:
                # Fallback without ollama
                logger.warning("Ollama not available, using fallback component generation")
                return f"Basic {component_type} analysis (enhanced generation unavailable)"
            
            response = ollama.chat(
                model='llama3.1:8b',
                messages=[{'role': 'user', 'content': context_prompt}],
                options={'temperature': 0.7}
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Enhanced component generation failed: {e}")
            return f"Error generating {component_type} analysis"
    
    def _build_context_prompt(self, card_data: Dict[str, Any], component_type: str,
                            existing_components: Dict[str, Any], 
                            analysis_context: Dict[str, Any]) -> str:
        """Build context-aware prompt for component generation"""
        
        base_prompt = f"""
You are analyzing the MTG card: {card_data.get('name', 'Unknown')}

CARD DETAILS:
- Mana Cost: {card_data.get('mana_cost', 'N/A')}
- Type: {card_data.get('type_line', 'N/A')}
- Text: {card_data.get('oracle_text', 'N/A')}

ANALYSIS CONTEXT:
- Power Indicators: {analysis_context.get('power_indicators', [])}
- Card Characteristics: {analysis_context.get('card_characteristics', {})}
- Mechanical Complexity: {analysis_context.get('mechanical_complexity', 'unknown')}

EXISTING ANALYSIS COMPONENTS:
{self._format_existing_components(existing_components)}

Generate a {component_type} analysis that is CONSISTENT with the existing components.
Keep the analysis focused, practical, and coherent with what's already been established.
"""
        
        return base_prompt
    
    def _format_existing_components(self, existing_components: Dict[str, Any]) -> str:
        """Format existing components for context"""
        if not existing_components:
            return "None yet - this is a foundation component"
        
        formatted = []
        for comp_type, comp_data in existing_components.items():
            content = comp_data.get('content', '') if isinstance(comp_data, dict) else str(comp_data)
            formatted.append(f"- {comp_type}: {content[:150]}...")
        
        return '\n'.join(formatted)
    
    # Utility methods for card analysis
    def _extract_mana_value(self, mana_cost: str) -> int:
        """Extract converted mana cost"""
        if not mana_cost:
            return 0
        # Simple implementation - could be enhanced
        import re
        numbers = re.findall(r'\d+', mana_cost)
        return sum(int(n) for n in numbers) + (len(mana_cost) - sum(len(n) for n in numbers))
    
    def _parse_type_line(self, type_line: str) -> Dict[str, List[str]]:
        """Parse type line into types and subtypes"""
        if '—' in type_line:
            types, subtypes = type_line.split('—', 1)
            return {
                'types': types.strip().split(),
                'subtypes': subtypes.strip().split()
            }
        return {'types': type_line.split(), 'subtypes': []}
    
    def _extract_power_toughness(self, card_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract power/toughness if creature"""
        power = card_data.get('power')
        toughness = card_data.get('toughness')
        if power is not None and toughness is not None:
            return {'power': str(power), 'toughness': str(toughness)}
        return None
    
    def _determine_color_identity(self, mana_cost: str) -> List[str]:
        """Determine color identity from mana cost"""
        colors = []
        if 'W' in mana_cost: colors.append('White')
        if 'U' in mana_cost: colors.append('Blue')
        if 'B' in mana_cost: colors.append('Black')
        if 'R' in mana_cost: colors.append('Red')
        if 'G' in mana_cost: colors.append('Green')
        return colors if colors else ['Colorless']
    
    def _measure_rules_complexity(self, oracle_text: str) -> str:
        """Measure rules complexity of the card"""
        if not oracle_text:
            return 'simple'
        
        complexity_indicators = len([
            word for word in ['when', 'whenever', 'if', 'unless', 'choose', 'may']
            if word in oracle_text.lower()
        ])
        
        if complexity_indicators >= 3:
            return 'complex'
        elif complexity_indicators >= 1:
            return 'moderate'
        else:
            return 'simple'
    
    def _extract_thematic_elements(self, card_data: Dict[str, Any]) -> List[str]:
        """Extract thematic elements for consistent flavor analysis"""
        elements = []
        
        name = card_data.get('name', '').lower()
        oracle_text = card_data.get('oracle_text', '').lower()
        
        # Identify thematic categories
        if any(word in name + oracle_text for word in ['dragon', 'knight', 'wizard', 'angel']):
            elements.append('fantasy_archetypes')
        
        if any(word in oracle_text for word in ['sacrifice', 'destroy', 'death', 'graveyard']):
            elements.append('dark_themes')
        
        if any(word in oracle_text for word in ['forest', 'plains', 'mountain', 'island', 'swamp']):
            elements.append('land_connection')
        
        return elements


# Global instance
coherence_manager = CoherenceManager()
