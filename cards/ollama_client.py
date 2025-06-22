"""
Ollama client for generating card analysis components using local LLM models.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)

# Model emoji mapping for logging
MODEL_EMOJIS = {
    'llama3.2:latest': '⚡',
    'llama3.1:latest': '⚖️', 
    'qwen2.5:7b-instruct-q4_0': '🚀',
    'mistral:7b': '🎯'
}

# The 4 Ollama models and their assigned component types
OLLAMA_MODELS = {
    'llama3.2:latest': {
        'name': 'Efficient Model',
        'use_case': 'Quick analysis, play tips, rules clarifications',
        'components': ['play_tips', 'mulligan_considerations', 'rules_clarifications']
    },    'llama3.1:latest': {
        'name': 'Balanced Model', 
        'use_case': 'Balanced analysis, synergies, competitive play',
        'components': ['thematic_analysis', 'synergy_analysis', 'competitive_analysis', 
                      'format_analysis', 'deck_archetypes', 'sideboard_guide', 'combo_suggestions']
    },'qwen2.5:7b-instruct-q4_0': {
        'name': 'Premium Model',
        'use_case': 'Deep analysis, complex interactions, investment',
        'components': ['tactical_analysis', 'power_level_assessment', 'meta_positioning',
                      'investment_outlook', 'advanced_interactions']
    },
    'mistral:7b': {
        'name': 'Alternative Perspective',
        'use_case': 'Budget options, education, historical context',
        'components': ['budget_alternatives', 'historical_context', 'new_player_guide',
                      'design_philosophy', 'art_flavor_analysis']
    }
}

# Map each component type to its assigned model
COMPONENT_MODEL_MAP = {}
for model, config in OLLAMA_MODELS.items():
    for component in config['components']:
        COMPONENT_MODEL_MAP[component] = model

# All 20 component types
ALL_COMPONENT_TYPES = [
    'tactical_analysis', 'thematic_analysis', 'play_tips',
    'combo_suggestions', 'power_level_assessment', 'format_analysis',
    'synergy_analysis', 'competitive_analysis', 'budget_alternatives',
    'historical_context', 'art_flavor_analysis', 'investment_outlook',
    'deck_archetypes', 'meta_positioning', 'new_player_guide',
    'advanced_interactions', 'mulligan_considerations', 'sideboard_guide',
    'rules_clarifications', 'design_philosophy'
]

class OllamaClient:
    """Client for interacting with local Ollama API to generate card analysis components."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
            return []
        except requests.RequestException:
            logger.error("Failed to get available models from Ollama")
            return []
    
    def generate_component(self, card_data: Dict, component_type: str) -> Optional[Dict]:
        """
        Generate a single analysis component for a card.
        
        Args:
            card_data: MongoDB card document
            component_type: Type of component to generate
            
        Returns:
            Dict with component data or None if failed
        """
        if component_type not in COMPONENT_MODEL_MAP:
            logger.error(f"Unknown component type: {component_type}")
            return None
        
        model = COMPONENT_MODEL_MAP[component_type]
        prompt = self._build_prompt(card_data, component_type)
        
        # Short, fun logging
        card_name = card_data.get('name', 'Unknown Card')
        model_emoji = MODEL_EMOJIS.get(model, '🤖')
        logger.info(f"{model_emoji} {component_type} → {card_name[:20]}{'...' if len(card_name) > 20 else ''}")        
        
        # Set timeout based on model complexity (2 min for Qwen quantized, 3 min for others)
        timeout = 120 if 'qwen2.5' in model else 180
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": "You are an expert Magic: The Gathering analyst. Write detailed, accurate analysis in markdown format.",
                    "stream": False,                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_ctx": 4096
                    }
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "").strip()
                
                if content:
                    return {
                        "content": content,
                        "model_used": model,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "word_count": len(content.split()),
                        "tokens_used": result.get("eval_count", 0)
                    }
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to generate component {component_type}: {e}")
            
        return None
    
    def _build_prompt(self, card_data: Dict, component_type: str) -> str:
        """Build component-specific prompt for the card."""
        
        # Extract card info
        name = card_data.get('name', 'Unknown Card')
        mana_cost = card_data.get('manaCost', '')
        type_line = card_data.get('type', '')
        oracle_text = card_data.get('text', '')
        power = card_data.get('power', '')
        toughness = card_data.get('toughness', '')
        
        # Base card context
        base_context = f"""
Card: {name}
Mana Cost: {mana_cost}
Type: {type_line}
"""
        
        if power and toughness:
            base_context += f"Power/Toughness: {power}/{toughness}\n"
            
        base_context += f"Oracle Text: {oracle_text}\n"
          # Component-specific prompts
        prompts = {
            'tactical_analysis': f"{base_context}\nProvide deep tactical analysis focusing on:\n- Optimal timing and sequencing\n- Key interactions and synergies\n- Play patterns and decision points\n- Situational considerations\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-500 words in markdown format.",
            
            'play_tips': f"{base_context}\nProvide 4-5 practical tips for playing this card effectively:\n- When to play it\n- What to watch out for\n- Common mistakes to avoid\n- Timing considerations\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write in bullet points, 200-300 words total.",
            
            'thematic_analysis': f"{base_context}\nAnalyze the thematic and flavor elements:\n- Lore and story connections\n- Flavor text significance\n- Thematic coherence with mechanics\n- Place in MTG's world-building\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 250-400 words in markdown format.",
            
            'synergy_analysis': f"{base_context}\nAnalyze card synergies and combinations:\n- Cards that work well with this\n- Archetype synergies\n- Combo potential\n- Anti-synergies to avoid\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in markdown format.",
            
            'competitive_analysis': f"{base_context}\nAnalyze competitive tournament viability:\n- Current meta positioning\n- Competitive formats where it's viable\n- Tournament results and trends\n- Competitive deck considerations\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-500 words in markdown format.",
            
            'format_analysis': f"{base_context}\nAnalyze performance across MTG formats:\n- Standard viability\n- Modern applications\n- Legacy/Vintage considerations\n- Commander/EDH role\n- Limited/Draft value\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 350-500 words in markdown format.",
            
            'power_level_assessment': f"{base_context}\nProvide comprehensive power level assessment:\n- Overall power rating (1-10)\n- Comparison to similar cards\n- Power level in different contexts\n- Historical power level perspective\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in markdown format.",
            
            'deck_archetypes': f"{base_context}\nIdentify suitable deck archetypes:\n- Primary deck types that want this card\n- Role in each archetype\n- Deck building considerations\n- Alternative inclusions\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in markdown format.",
            
            'sideboard_guide': f"{base_context}\nProvide sideboarding strategies:\n- When to sideboard in/out\n- Matchups where it's important\n- Sideboard card interactions\n- Meta-specific considerations\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 250-400 words in markdown format.",
            
            'mulligan_considerations': f"{base_context}\nAnalyze mulligan decisions involving this card:\n- When to keep hands with this card\n- When to mulligan it away\n- Hand quality evaluation\n- Opening hand priorities\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 200-350 words in markdown format.",
            
            'combo_suggestions': f"{base_context}\nSuggest card combinations and combos:\n- Direct combo pieces\n- Synergistic packages\n- Engine components\n- Win condition setups\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in markdown format.",
            
            'budget_alternatives': f"{base_context}\nSuggest budget-friendly alternatives:\n- Cheaper cards with similar effects\n- Budget deck considerations\n- Cost-effective substitutions\n- Performance trade-offs\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 250-400 words in markdown format.",
            
            'new_player_guide': f"{base_context}\nExplain this card for new players:\n- Basic functionality explained simply\n- Why it's good/bad for beginners\n- Learning opportunities it provides\n- Common beginner mistakes\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in accessible language. Write in markdown format.",
            
            'rules_clarifications': f"{base_context}\nClarify rules and common questions:\n- Complex rules interactions\n- Common misconceptions\n- Timing rules\n- Edge cases and rulings\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 250-400 words in clear, instructional format. Write in markdown format.",
            
            'historical_context': f"{base_context}\nProvide historical context:\n- When it was printed and why\n- Meta impact when released\n- Design evolution it represents\n- Historical significance in MTG\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in markdown format.",
            
            'art_flavor_analysis': f"{base_context}\nAnalyze art and flavor elements:\n- Artistic style and techniques\n- Flavor text analysis\n- Visual storytelling\n- Aesthetic contribution to the set\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 250-400 words in markdown format.",
            
            'design_philosophy': f"{base_context}\nAnalyze the design philosophy:\n- Design goals and intentions\n- Mechanical innovation\n- Balance considerations\n- Design space exploration\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words in markdown format.",
            
            'investment_outlook': f"{base_context}\nAnalyze financial and collectible aspects:\n- Current market trends\n- Long-term value prospects\n- Collectibility factors\n- Reprint considerations\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-450 words. Focus on game impact over financial advice.  Write in markdown format.",
            
            'meta_positioning': f"{base_context}\nAnalyze current metagame positioning:\n- Role in current meta\n- Matchup considerations\n- Meta shifts that affect it\n- Adaptation potential\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 300-500 words in markdown format.",
            
            'advanced_interactions': f"{base_context}\nExplore advanced rules interactions:\n- Complex edge cases\n- Layer system interactions\n- Timing and priority issues\n- Judge call scenarios\nAlways enclose card names in [[ card name ]] double square brackets to make card parsing easier. Write 350-500 words with specific examples.  Write in markdown format."
        }
        
        return prompts.get(component_type, f"{base_context}\nProvide analysis of this card focusing on {component_type.replace('_', ' ')}.")

# Convenience function for external use
def get_component_model(component_type: str) -> Optional[str]:
    """Get the assigned model for a component type."""
    return COMPONENT_MODEL_MAP.get(component_type)
