#!/usr/bin/env python3
"""
Desktop Worker - Remote MongoDB Ready
Handles GPU-accelerated fast analysis components with remote database support
"""

import json
import time
import requests
import socket
import platform
import psutil
import ollama
import os
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesktopWorker:
    """Worker optimized for GPU-based fast analysis components"""
    
    def __init__(self, server_url: str = None):
        # Use environment variable or default
        self.server_url = server_url or os.getenv('SWARM_SERVER_URL', 'http://localhost:8001')
        self.worker_id = f"desktop-{socket.gethostname()}"
        self.capabilities = self._detect_capabilities()
        self.running = False
        self.selected_model = self._select_best_model()
        
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
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _select_best_model(self) -> str:
        """Select the best available model for this worker"""
        preferred_models = ['qwen2.5:7b', 'llama3.1:latest', 'mistral:7b']
        
        try:
            # Get available models
            models = ollama.list()
            available_model_names = [model['name'] for model in models['models']]
            
            # Select first preferred model that's available
            for model in preferred_models:
                if model in available_model_names:
                    logger.info(f"🎯 Using model: {model}")
                    return model
            
            # Fallback to first available model
            if available_model_names:
                fallback = available_model_names[0]
                logger.info(f"🎯 Using fallback model: {fallback}")
                return fallback
                
        except Exception as e:
            logger.error(f"Model selection error: {e}")
        
        # Final fallback
        return 'llama3.1:latest'
    
    def register(self) -> bool:
        """Register with the central server"""
        try:
            logger.info(f"🤖 Registering worker: {self.worker_id}")
            response = requests.post(
                f"{self.server_url}/cards/api/swarm/register",
                json={
                    'worker_id': self.worker_id,
                    'capabilities': self.capabilities
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Registration successful!")
                logger.info(f"   Assigned components: {len(result['assigned_components'])}")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
    
    def get_work(self) -> List[Dict[str, Any]]:
        """Request work from the server"""
        try:
            response = requests.post(
                f"{self.server_url}/cards/api/swarm/get_work",
                json={
                    'worker_id': self.worker_id,
                    'max_tasks': 2  # Desktop can handle multiple tasks
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tasks = result.get('tasks', [])
                if tasks:
                    logger.info(f"📋 Received {len(tasks)} tasks")
                return tasks
            else:
                logger.error(f"Work request failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Work request error: {e}")
            return []
    
    def generate_analysis(self, card_data: Dict, components: List[str]) -> Dict[str, str]:
        """Generate analysis using Ollama"""
        results = {}
        
        for component in components:
            logger.info(f"🔥 Generating {component} for {card_data.get('name')}")
            
            # Create component-specific prompt
            analysis = self._generate_component_analysis(card_data, component)
            results[component] = analysis
            
            logger.info(f"✅ Completed {component} ({len(analysis)} chars)")
        
        return results
    
    def _generate_component_analysis(self, card_data: Dict, component: str) -> str:
        """Generate specific component analysis using Ollama"""
        card_name = card_data.get('name', 'Unknown Card')
        mana_cost = card_data.get('mana_cost', 'N/A')
        type_line = card_data.get('type_line', 'N/A')
        oracle_text = card_data.get('oracle_text', 'N/A')
        
        prompts = {
            'play_tips': f"""Analyze the Magic: The Gathering card "{card_name}" for practical gameplay tips.

Card Details:
- Name: {card_name}
- Mana Cost: {mana_cost}
- Type: {type_line}
- Text: {oracle_text}

Provide 3-4 practical gameplay tips. Focus on when to play it, optimal timing, and tactical considerations.""",

            'rules_clarifications': f"""Explain the rules and interactions for "{card_name}".

Card Details:
- Name: {card_name}
- Mana Cost: {mana_cost}
- Type: {type_line}
- Text: {oracle_text}

Cover any complex rules interactions, edge cases, and common misconceptions.""",

            'combo_suggestions': f"""Suggest combinations and synergies for "{card_name}".

Card Details:
- Name: {card_name}
- Mana Cost: {mana_cost}
- Type: {type_line}
- Text: {oracle_text}

Include both competitive and casual synergies, focusing on practical deck building advice.""",

            'format_analysis': f"""Analyze "{card_name}" across different Magic formats.

Card Details:
- Name: {card_name}
- Mana Cost: {mana_cost}
- Type: {type_line}
- Text: {oracle_text}

Discuss performance in Standard, Modern, Legacy, Commander, and other relevant formats.""",

            'competitive_analysis': f"""Evaluate the competitive viability of "{card_name}".

Card Details:
- Name: {card_name}
- Mana Cost: {mana_cost}
- Type: {type_line}
- Text: {oracle_text}

Assess tournament potential, meta positioning, and competitive strengths/weaknesses.""",

            'tactical_analysis': f"""Provide deep tactical analysis of "{card_name}".

Card Details:
- Name: {card_name}
- Mana Cost: {mana_cost}
- Type: {type_line}
- Text: {oracle_text}

Cover strategic applications, game theory considerations, and advanced tactical uses."""
        }
        
        prompt = prompts.get(component, f"Analyze {card_name} for {component}")
        
        try:
            response = ollama.generate(
                model=self.selected_model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'num_predict': 400
                }
            )
            return response['response']
            
        except Exception as e:
            logger.error(f"Generation error for {component}: {e}")
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
                        'worker_type': 'desktop',
                        'model': self.selected_model,
                        'gpu_used': self.capabilities['gpu_available']
                    }
                }
            }
            
            response = requests.post(
                f"{self.server_url}/cards/api/swarm/submit_results",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Submitted task {task_id}")
                return True
            else:
                logger.error(f"Submission failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Submission error: {e}")
            return False
    
    def run(self):
        """Main worker loop"""
        logger.info(f"🚀 Starting desktop worker: {self.worker_id}")
        logger.info(f"🎯 Using model: {self.selected_model}")
        logger.info(f"⚡ GPU available: {self.capabilities['gpu_available']}")
        
        # Register with server
        if not self.register():
            logger.error("Failed to register, exiting")
            return
        
        self.running = True
        
        while self.running:
            try:
                # Get work
                tasks = self.get_work()
                
                if not tasks:
                    logger.info("⏳ No work available, waiting...")
                    time.sleep(30)
                    continue
                
                # Process tasks
                for task in tasks:
                    start_time = time.time()
                    
                    logger.info(f"🎯 Processing: {task['card_name']} - {task['components']}")
                    
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
                        logger.info(f"🎉 Completed {task['card_name']} in {execution_time:.2f}s")
                    else:
                        logger.error(f"Failed to submit {task['task_id']}")
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("Desktop worker shutting down")

if __name__ == "__main__":
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    worker = DesktopWorker(server_url)
    worker.run()
