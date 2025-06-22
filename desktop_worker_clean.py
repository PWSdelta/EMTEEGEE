#!/usr/bin/env python3
"""
Desktop Worker (RTX 3070 + 64GB RAM) - Clean Version
Handles GPU-accelerated fast analysis components with real Ollama integration
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
            'gpu_available': True,  # Desktop has GPU
            'worker_type': 'desktop',
            'preferred_models': ['qwen2.5:7b', 'llama3.1:latest', 'mistral:7b'],
            'specialization': 'fast_gpu_inference'
        }
        return capabilities
    
    def _select_best_model(self) -> str:
        """Select the best available model for this worker"""
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            
            # Prefer models in order
            for preferred in self.capabilities['preferred_models']:
                if preferred in available_models:
                    logger.info(f"🎯 Using model: {preferred}")
                    return preferred
            
            # Fallback to first available model
            if available_models:
                model = available_models[0]
                logger.info(f"🎯 Using fallback model: {model}")
                return model
            
            logger.error("❌ No models available")
            return "llama3.1:latest"  # Default fallback
            
        except Exception as e:
            logger.error(f"Model selection error: {e}")
            return "llama3.1:latest"  # Default fallback
    
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
                logger.info(f"✅ Registration successful!")
                logger.info(f"   Assigned components: {len(result['assigned_components'])}")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
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
                logger.error(f"❌ Work request failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Work request error: {e}")
            return []
    
    def generate_analysis(self, card_data: Dict, components: List[str]) -> Dict[str, str]:
        """Generate analysis using GPU-optimized models"""
        results = {}
        
        for component in components:
            logger.info(f"🔥 Generating {component} for {card_data.get('name')}")
            
            try:
                analysis = self._generate_component_analysis(card_data, component)
                results[component] = analysis
                logger.info(f"✅ Completed {component} ({len(analysis)} chars)")
                
            except Exception as e:
                logger.error(f"❌ Failed to generate {component}: {e}")
                results[component] = f"Error generating {component}: {str(e)}"
        
        return results
    
    def _generate_component_analysis(self, card_data: Dict, component: str) -> str:
        """Generate specific component analysis using Ollama"""
        card_name = card_data.get('name', 'Unknown')
        
        # Component-specific prompts optimized for fast generation
        prompts = {
            'play_tips': f'''Provide 3-4 concise gameplay tips for "{card_name}":

Card: {card_data.get('oracle_text', '')}
Mana Cost: {card_data.get('mana_cost', 'N/A')}
Type: {card_data.get('type_line', 'N/A')}

Focus on:
1. When to play it
2. Best targets/timing
3. Common synergies

Be practical and concise.''',

            'rules_clarifications': f'''Explain key rules interactions for "{card_name}":

Card text: {card_data.get('oracle_text', '')}

Cover:
1. Any complex mechanics
2. Common misunderstandings
3. Stack interactions
4. Timing restrictions

Be clear and accurate.''',

            'combo_suggestions': f'''Suggest card combinations for "{card_name}":

Card: {card_data.get('oracle_text', '')}
Type: {card_data.get('type_line', 'N/A')}

Provide:
1. 2-3 specific combo cards
2. How the synergy works
3. Format applicability

Focus on practical combinations.''',
        }
        
        prompt = prompts.get(component, f"Analyze {card_name} for {component}. Be concise and helpful.")
        
        # Generate with Ollama
        response = ollama.generate(
            model=self.selected_model,
            prompt=prompt,
            options={
                'temperature': 0.7,
                'num_predict': 200
            }
        )
        
        return response['response']
    
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
                        'model': self.selected_model,
                        'worker_type': 'desktop',
                        'gpu_used': True,
                        'inference_backend': 'ollama'
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
                logger.error(f"❌ Submission failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
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
            logger.error("❌ Failed to register, exiting")
            return
        
        self.running = True
        
        while self.running:
            try:
                # Get work
                tasks = self.get_work()
                
                if not tasks:
                    logger.info("😴 No work available, waiting...")
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
                        logger.error(f"❌ Failed to submit {task['card_name']}")
                
            except KeyboardInterrupt:
                logger.info("⛔ Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("👋 Desktop worker shutting down")

if __name__ == "__main__":
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    
    worker = DesktopWorker(server_url)
    worker.run()
