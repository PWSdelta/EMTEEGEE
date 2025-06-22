#!/usr/bin/env python3
"""
Desktop Worker with Real Ollama Integration (GPU Models)
RTX 3070 + 64GB RAM - Fast 7B models for quick analysis
qwen2.5:7b, llama3.1:latest, mistral:7b
"""

import json
import time
import requests
import socket
import platform
import psutil
import subprocess
import ollama
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesktopWorkerReal:
    """Worker optimized for GPU-based fast analysis components with real Ollama models"""
      def __init__(self, server_url: str = "https://emteegee.tcgplex.com"):
        self.server_url = server_url
        self.worker_id = f"desktop-{socket.gethostname()}"
        self.capabilities = self._detect_capabilities()
        self.running = False
        
        # Desktop model preferences (7B models for speed)
        self.preferred_models = ['qwen2.5:7b', 'llama3.1:latest', 'mistral:7b']
        self.active_model = self._select_best_model()
        
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Auto-detect hardware capabilities"""
        capabilities = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'cpu_cores': psutil.cpu_count(),
            'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
            'gpu_available': self._check_gpu(),
            'worker_type': 'desktop',
            'preferred_models': ['qwen2.5:7b', 'llama3.1:latest', 'mistral:7b'],
            'specialization': 'fast_gpu_inference'
        }
        return capabilities
    
    def _check_gpu(self) -> bool:
        """Check if NVIDIA GPU is available"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
      def _select_best_model(self) -> str:
        """Select the best available model for this worker"""
        try:
            models_response = ollama.list()
            available_models = []
            
            # Handle different response formats
            if isinstance(models_response, dict):
                if 'models' in models_response:
                    available_models = [model.get('name', '') for model in models_response['models'] if model.get('name')]
                else:
                    available_models = [model.get('name', '') for model in models_response.get('data', []) if model.get('name')]
            
            logger.info(f"Available models: {available_models}")
            
            for preferred in self.preferred_models:
                if preferred in available_models:
                    logger.info(f"Selected model: {preferred}")
                    return preferred
            
            # Fallback to first available model
            if available_models:
                model = available_models[0]
                logger.info(f"Using fallback model: {model}")
                return model
            
            raise Exception("No models available")
            
        except Exception as e:
            logger.error(f"Model selection error: {e}")
            return "llama3.1:latest"  # Default fallback
    
    def register(self) -> bool:
        """Register with the central server"""
        try:            response = requests.post(
                f"{self.server_url}/cards/api/swarm/register",
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
        try:            response = requests.post(
                f"{self.server_url}/cards/api/swarm/get_work",
                json={
                    'worker_id': self.worker_id,
                    'max_tasks': 2  # Desktop can handle multiple tasks
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
        """Generate analysis using real Ollama models"""
        results = {}
        
        for component in components:
            logger.info(f"Generating {component} for {card_data.get('name')} using {self.active_model}")
            
            try:
                analysis = self._generate_component_analysis(card_data, component)
                results[component] = analysis
                logger.info(f"✅ Generated {component} ({len(analysis)} chars)")
                
            except Exception as e:
                logger.error(f"❌ Failed to generate {component}: {e}")
                results[component] = f"Error generating {component}: {str(e)}"
        
        return results
    
    def _generate_component_analysis(self, card_data: Dict, component: str) -> str:
        """Generate specific component analysis using Ollama"""
        card_name = card_data.get('name', 'Unknown Card')
        mana_cost = card_data.get('mana_cost', '')
        type_line = card_data.get('type_line', '')
        oracle_text = card_data.get('oracle_text', '')
        power = card_data.get('power', '')
        toughness = card_data.get('toughness', '')
        
        # Build card context
        card_context = f"""
Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
"""
        if power and toughness:
            card_context += f"Power/Toughness: {power}/{toughness}\n"
        
        # Component-specific prompts optimized for fast analysis
        prompts = {
            'play_tips': f"""Analyze this Magic: The Gathering card and provide 3-5 practical gameplay tips:

{card_context}

Focus on:
- Optimal timing for playing this card
- Key interactions to look for
- Common mistakes to avoid
- Situational considerations

Provide concise, actionable advice.""",
            
            'rules_clarifications': f"""Analyze this Magic card and explain any complex rules interactions:

{card_context}

Cover:
- How the card's abilities work mechanically
- Common rules questions players have
- Interactions with other common cards
- Stack and timing considerations

Be precise and clear.""",
            
            'combo_suggestions': f"""Suggest card combinations and synergies for this Magic card:

{card_context}

Provide:
- 3-4 specific card synergies
- Format considerations (Standard, Modern, Commander)
- Both competitive and casual options
- Brief explanation of each combo

Focus on practical, playable combinations.""",
            
            'format_analysis': f"""Analyze this card's performance across Magic formats:

{card_context}

Evaluate:
- Standard viability and meta position
- Modern playability and archetype fit
- Legacy/Vintage considerations
- Commander utility and power level

Provide format-specific insights.""",
            
            'competitive_analysis': f"""Evaluate this card's competitive tournament potential:

{card_context}

Analyze:
- Current meta positioning
- Competitive archetype applications
- Sideboard considerations
- Tournament-level power assessment

Focus on competitive viability.""",
            
            'tactical_analysis': f"""Provide tactical analysis for competitive play:

{card_context}

Cover:
- Strategic applications in gameplay
- Decision-making considerations
- Resource management implications
- Game theory applications

Focus on high-level strategic thinking."""
        }
        
        prompt = prompts.get(component, f"Provide detailed analysis of {card_name} focusing on {component}")
        
        try:
            # Use Ollama to generate the analysis
            response = ollama.generate(
                model=self.active_model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 500  # Keep responses focused
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error generating analysis with Ollama: {str(e)}"
    
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
                        'worker_type': 'desktop',
                        'gpu_used': True,
                        'model_name': self.active_model,
                        'model_size': '7B',
                        'inference_backend': 'ollama_gpu'
                    }
                }
            }
              response = requests.post(
                f"{self.server_url}/cards/api/swarm/submit_results",
                json=payload,
                timeout=60
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
        logger.info(f"🚀 Starting desktop worker: {self.worker_id}")
        logger.info(f"🎯 Using model: {self.active_model}")
        logger.info(f"⚡ GPU available: {self.capabilities['gpu_available']}")
        
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
                    time.sleep(30)
                    continue
                
                # Process tasks
                for task in tasks:
                    start_time = time.time()
                    
                    logger.info(f"🔥 Processing task {task['task_id']} for card {task['card_name']}")
                    logger.info(f"📝 Components: {task['components']}")
                    
                    # Generate analysis
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
                        logger.info(f"🎉 Completed task {task['task_id']} in {execution_time:.2f}s")
                    else:
                        logger.error(f"💥 Failed to submit task {task['task_id']}")
                
            except KeyboardInterrupt:
                logger.info("🛑 Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"💥 Worker error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("👋 Desktop worker shutting down")

if __name__ == "__main__":
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "https://emteegee.tcgplex.com"
    
    worker = DesktopWorkerReal(server_url)
    worker.run()
