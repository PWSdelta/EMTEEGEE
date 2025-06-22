#!/usr/bin/env python3
"""
Laptop Worker (128GB RAM, Big CPU)
Handles CPU-intensive large model analysis components
"""

import json
import time
import requests
import socket
import platform
import psutil
import multiprocessing
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LaptopWorker:
    """Worker optimized for CPU-intensive large model analysis"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.worker_id = f"laptop-{socket.gethostname()}"
        self.capabilities = self._detect_capabilities()
        self.running = False
        
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Auto-detect hardware capabilities"""
        capabilities = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'cpu_cores': psutil.cpu_count(),
            'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
            'gpu_available': False,  # Using CPU for large models
            'worker_type': 'laptop',
            'preferred_models': ['mixtral-8x7b', 'llama-2-70b', 'claude-style-large'],
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
            logger.info(f"Generating deep {component} analysis for {card_data.get('name')}")
            
            # Use all available CPU cores for large model inference
            analysis = self._generate_deep_component_analysis(card_data, component)
            results[component] = analysis
            
            time.sleep(5)  # Large models take longer
        
        return results
    
    def _generate_deep_component_analysis(self, card_data: Dict, component: str) -> str:
        """Generate deep, nuanced component analysis"""
        card_name = card_data.get('name', 'Unknown Card')
        oracle_text = card_data.get('oracle_text', '')
        
        deep_prompts = {
            'thematic_analysis': f"""Provide an in-depth thematic and narrative analysis of {card_name}.
            Examine the card's flavor text, art description, and mechanical design in the context of Magic's lore.
            Discuss its place in the multiverse, connections to other cards, and storytelling elements.
            Oracle text: {oracle_text}""",
            
            'historical_context': f"""Analyze the historical impact and significance of {card_name} in Magic's development.
            Discuss its influence on game design, meta evolution, and cultural impact within the Magic community.
            Compare its power level to cards from different eras and explain design philosophy changes.
            Oracle text: {oracle_text}""",
            
            'design_philosophy': f"""Examine the design philosophy behind {card_name} from a game designer's perspective.
            Analyze color pie placement, complexity considerations, and intended play patterns.
            Discuss balance considerations and how it fits into Magic's overall design framework.
            Oracle text: {oracle_text}""",
            
            'advanced_interactions': f"""Provide comprehensive analysis of complex interactions involving {card_name}.
            Cover edge cases, stack interactions, replacement effects, and tournament-level rule nuances.
            Include examples with multiple cards and layered effects.
            Oracle text: {oracle_text}""",
            
            'art_flavor_analysis': f"""Conduct detailed analysis of {card_name}'s artistic and flavor elements.
            Examine the visual storytelling, artistic techniques, and how art reinforces mechanical identity.
            Discuss the artist's style and how it contributes to Magic's visual language.
            Oracle text: {oracle_text}""",
            
            'meta_positioning': f"""Analyze {card_name}'s positioning within various competitive metagames.
            Discuss its role evolution, adaptation to meta shifts, and strategic applications.
            Compare performance across different competitive environments and explain meta-dependent value.
            Oracle text: {oracle_text}"""
        }
        
        prompt = deep_prompts.get(component, f"Provide deep analysis of {card_name} for {component}")
        
        # Simulate large model CPU inference
        return f"[CPU-Generated Deep Analysis for {component}]\n\n{prompt}\n\n[This would be generated using a 70B+ model with extensive reasoning and context awareness]"
    
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
                        'gpu_used': False,
                        'model_size': '70B+',
                        'inference_backend': 'cpu_optimized',
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
                logger.info(f"Successfully submitted task {task_id}")
                return True
            else:
                logger.error(f"Submission failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Submission error: {e}")
            return False
    
    def run(self):
        """Main worker loop"""
        logger.info(f"Starting laptop worker: {self.worker_id}")
        
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
                    logger.info("No work available, waiting...")
                    time.sleep(45)
                    continue
                
                # Process tasks (one at a time for deep analysis)
                for task in tasks:
                    start_time = time.time()
                    
                    logger.info(f"Processing deep analysis task {task['task_id']} for card {task['card_name']}")
                    
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
                        logger.info(f"Completed deep analysis task {task['task_id']} in {execution_time:.2f}s")
                    else:
                        logger.error(f"Failed to submit task {task['task_id']}")
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(15)  # Wait before retrying
        
        logger.info("Laptop worker shutting down")

if __name__ == "__main__":
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    worker = LaptopWorker(server_url)
    worker.run()
