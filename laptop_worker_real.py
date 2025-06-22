#!/usr/bin/env python3
"""
Laptop Worker with Large CPU Models
128GB RAM, Big CPU - Large models for deep analysis
mixtral:8x7b, llama3.3:70b
"""

import json
import time
import requests
import socket
import platform
import psutil
import multiprocessing
import ollama
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LaptopWorkerReal:
    """Laptop worker using large CPU models via Ollama for deep analysis"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.worker_id = f"laptop-{socket.gethostname()}"
        self.capabilities = self._detect_capabilities()
        self.running = False
        
        # Large CPU models for laptop (your models)
        self.preferred_models = ['mixtral:8x7b', 'llama3.3:70b']
        self.current_model = 'mixtral:8x7b'  # Default to Mixtral for CPU
        
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Auto-detect hardware capabilities"""
        capabilities = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'cpu_cores': psutil.cpu_count(),
            'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
            'gpu_available': False,  # Using CPU for large models
            'worker_type': 'laptop',
            'preferred_models': ['mixtral:8x7b', 'llama3.3:70b'],
            'specialization': 'deep_analysis_cpu'
        }
        return capabilities
    
    def register(self) -> bool:
        """Register with the central server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/swarm/register",
                json={
                    'worker_id': self.worker_id,
                    'capabilities': self.capabilities
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Registered successfully: {result}")
                return True
            else:
                logger.error(f"Registration failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
    
    def get_work(self) -> List[Dict[str, Any]]:
        """Request work from the server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/swarm/get_work",
                json={
                    'worker_id': self.worker_id,
                    'max_tasks': 1  # Laptop takes fewer but deeper tasks
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('tasks', [])
            else:
                logger.error(f"Work request failed: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Work request error: {e}")
            return []
    
    def generate_analysis(self, card_data: Dict, components: List[str]) -> Dict[str, str]:
        """Generate deep analysis using large CPU models"""
        results = {}
        
        for component in components:
            logger.info(f"🧠 CPU Generating deep {component} for {card_data.get('name')} using {self.current_model}")
            
            # Generate with large model
            analysis = self._generate_deep_component_with_ollama(card_data, component)
            results[component] = analysis
        
        return results
    
    def _generate_deep_component_with_ollama(self, card_data: Dict, component: str) -> str:
        """Generate deep, nuanced component analysis using large Ollama models"""
        card_name = card_data.get('name', 'Unknown Card')
        mana_cost = card_data.get('mana_cost', 'N/A')
        type_line = card_data.get('type_line', 'N/A')
        oracle_text = card_data.get('oracle_text', 'N/A')
        power = card_data.get('power', 'N/A')
        toughness = card_data.get('toughness', 'N/A')
        
        # Deep analysis prompts for large models
        deep_prompts = {
            'thematic_analysis': f"""Conduct an in-depth thematic and narrative analysis of this Magic: The Gathering card:

Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
P/T: {power}/{toughness}

Provide comprehensive analysis covering:
1. **Flavor and Lore**: Examine the card's place in Magic's multiverse, story connections, and world-building elements
2. **Mechanical-Flavor Alignment**: How the game mechanics reflect the thematic concept
3. **Art and Flavor Text**: Visual storytelling and narrative elements (if applicable)
4. **Cultural and Mythological References**: Real-world inspirations and references
5. **Character Development**: If this represents a character, analyze their role and evolution
6. **Plane and Setting**: How this fits into Magic's various planes and settings

Write in an engaging, educational style that helps players appreciate the rich storytelling aspects of Magic.""",

            'historical_context': f"""Analyze the historical impact and significance of this Magic: The Gathering card:

Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
P/T: {power}/{toughness}

Provide detailed historical analysis:
1. **Design Era Context**: What design philosophy and constraints existed when this was created
2. **Meta Impact**: How this card influenced competitive play and deck construction
3. **Power Level Evolution**: How this compares to cards from different eras
4. **Rules Evolution**: Any rules changes or clarifications this card prompted
5. **Reprints and Variations**: History of different printings and their impact
6. **Community Reception**: How players and the community responded to this card
7. **Legacy Influence**: How this card influenced future card designs

Be thorough and provide specific examples and comparisons.""",

            'design_philosophy': f"""Examine the game design philosophy behind this Magic: The Gathering card:

Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
P/T: {power}/{toughness}

Analyze from a game designer's perspective:
1. **Color Pie Placement**: Why this effect belongs in these colors
2. **Mana Cost Philosophy**: How the cost reflects the power level and design intent
3. **Complexity Considerations**: Complexity vs. gameplay depth trade-offs
4. **Play Pattern Design**: What gameplay experiences this creates
5. **Format Considerations**: How this was designed for different play environments
6. **Balance Philosophy**: Risk/reward structures and counterplay options
7. **Innovation Elements**: New or unique design elements introduced
8. **Player Psychographics**: Which player types this appeals to (Timmy/Johnny/Spike)

Provide insights that would interest both players and aspiring game designers.""",

            'advanced_interactions': f"""Provide comprehensive analysis of complex interactions involving this Magic card:

Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
P/T: {power}/{toughness}

Cover advanced interaction scenarios:
1. **Stack Interactions**: Complex ordering and response scenarios
2. **Replacement Effects**: How this interacts with replacement and prevention effects
3. **Layering System**: Continuous effects and dependency ordering
4. **State-Based Actions**: Timing of state-based checks with this card
5. **Multiple Card Interactions**: Complex scenarios with 3+ interacting cards
6. **Edge Cases**: Unusual situations and corner case rulings
7. **Tournament Implications**: Competitive play considerations and judge calls
8. **Rules Updates**: How changing rules have affected this card's function

Include specific examples and step-by-step breakdowns of complex scenarios.""",

            'art_flavor_analysis': f"""Conduct detailed analysis of the artistic and flavor elements of this Magic card:

Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}

Analyze the artistic and flavor dimensions:
1. **Visual Composition**: Art style, color palette, and visual design choices
2. **Flavor Text Analysis**: Literary devices, tone, and narrative contribution
3. **Mechanical-Flavor Synergy**: How art and mechanics reinforce each other
4. **Artist's Style**: Contribution to Magic's visual language and artistic evolution
5. **Symbolic Elements**: Hidden meanings, symbolism, and visual metaphors
6. **Cultural Representation**: How this represents different cultures or archetypes
7. **Emotional Impact**: The mood and feelings the art evokes
8. **Collectible Art Value**: Artistic significance beyond gameplay

Write with appreciation for both the artistic craft and its role in the game.""",

            'meta_positioning': f"""Analyze this card's positioning within competitive metagames:

Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
P/T: {power}/{toughness}

Provide comprehensive meta analysis:
1. **Current Meta Role**: Position in today's competitive environments
2. **Meta Evolution**: How its role has changed over time
3. **Deck Archetypes**: Specific strategies that utilize this card
4. **Meta Dependency**: How meta shifts affect this card's viability
5. **Sideboard Considerations**: Situational value and boarding strategies
6. **Format Differences**: Performance variations across different formats
7. **Tech Card Potential**: Niche applications and surprise factor
8. **Future Meta Predictions**: Potential for meta changes to affect relevance

Focus on strategic depth and competitive insights."""
        }
        
        prompt = deep_prompts.get(component, f"Provide deep analysis of the MTG card {card_name} for {component}")
        
        try:
            # Use large Ollama model for deep analysis
            response = ollama.chat(
                model=self.current_model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.8,  # Slightly higher for creativity
                    'top_p': 0.9,
                    'num_ctx': 4096,  # Larger context for deep analysis
                    'num_predict': 1000,  # Allow longer responses
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error generating {component} analysis: {str(e)}"
    
    def submit_results(self, task_id: str, results: Dict[str, str], execution_time: float) -> bool:
        """Submit completed analysis to server"""
        try:
            payload = {
                'worker_id': self.worker_id,
                'task_id': task_id,
                'results': {
                    'components': results,
                    'execution_time': execution_time,
                    'model_info': {
                        'worker_type': 'laptop',
                        'model_used': self.current_model,
                        'gpu_used': False,
                        'model_size': '70B' if '70b' in self.current_model else '8x7B',
                        'inference_backend': 'ollama_cpu',
                        'cpu_cores_used': multiprocessing.cpu_count()
                    }
                }
            }
            
            response = requests.post(
                f"{self.server_url}/api/swarm/submit_results",
                json=payload,
                timeout=120  # Longer timeout for large results
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully submitted task {task_id}")
                return True
            else:
                logger.error(f"❌ Submission failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Submission error: {e}")
            return False
    
    def run(self):
        """Main worker loop"""
        logger.info(f"🧠 Starting large model laptop worker: {self.worker_id}")
        logger.info(f"🎯 Using model: {self.current_model}")
        
        # Test Ollama connection
        try:
            ollama.list()
            logger.info("✅ Ollama connection successful")
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            return
        
        # Register with server
        if not self.register():
            logger.error("❌ Failed to register, exiting")
            return
        
        self.running = True
        
        while self.running:
            try:
                # Get work
                tasks = self.get_work()
                
                if not tasks:
                    logger.info("💤 No work available, waiting...")
                    time.sleep(45)
                    continue
                
                # Process tasks (one at a time for deep analysis)
                for task in tasks:
                    start_time = time.time()
                    
                    logger.info(f"🚀 Processing deep analysis task {task['task_id']} for card {task['card_name']}")
                    logger.info(f"📝 Components: {task['components']}")
                    
                    # Generate deep analysis
                    results = self.generate_analysis(
                        task['card_data'], 
                        task['components']
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Submit results
                    success = self.submit_results(
                        task['task_id'], 
                        results, 
                        execution_time
                    )
                    
                    if success:
                        logger.info(f"🎉 Completed deep analysis task {task['task_id']} in {execution_time:.2f}s")
                    else:
                        logger.error(f"❌ Failed to submit task {task['task_id']}")
                
            except KeyboardInterrupt:
                logger.info("🛑 Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                time.sleep(15)  # Wait before retrying
        
        logger.info("👋 Laptop worker shutting down")

if __name__ == "__main__":
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    worker = LaptopWorkerReal(server_url)
    worker.run()
