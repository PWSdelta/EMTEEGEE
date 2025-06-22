#!/usr/bin/env python3
"""
Desktop Worker (RTX 3070 + 64GB RAM)
Handles GPU-accelerated fast analysis components
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

class DesktopWorker:
    """Worker optimized for GPU-based fast analysis components"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.worker_id = f"desktop-{socket.gethostname()}"
        self.capabilities = self._detect_capabilities()
        self.running = False
        
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Auto-detect hardware capabilities"""
        capabilities = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'cpu_cores': psutil.cpu_count(),
            'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
            'gpu_available': self._check_gpu(),
            'worker_type': 'desktop',
            'preferred_models': ['llama-3.1-8b', 'phi-3-medium', 'codestral-7b'],
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
        """Generate analysis using GPU-optimized models"""
        results = {}
        
        for component in components:
            logger.info(f"Generating {component} for {card_data.get('name')}")
            
            # This is where you'd integrate your actual LLM inference
            # For now, simulating with targeted prompts per component
            analysis = self._generate_component_analysis(card_data, component)
            results[component] = analysis
            
            time.sleep(2)  # Simulate processing time
        
        return results
    
    def _generate_component_analysis(self, card_data: Dict, component: str) -> str:
        """Generate specific component analysis"""
        card_name = card_data.get('name', 'Unknown Card')
        
        prompts = {
            'play_tips': f"Provide practical gameplay tips for {card_name}. Focus on when to play it, optimal timing, and tactical considerations.",
            'rules_clarifications': f"Explain any complex rules interactions for {card_name}. Cover edge cases and common misconceptions.",
            'combo_suggestions': f"Suggest card combinations and synergies for {card_name}. Include both competitive and casual options.",
            'format_analysis': f"Analyze {card_name}'s performance across different Magic formats (Standard, Modern, Legacy, Commander).",
            'competitive_analysis': f"Evaluate {card_name}'s competitive viability, meta positioning, and tournament potential.",
            'tactical_analysis': f"Provide deep tactical analysis of {card_name}, covering strategic applications and game theory."
        }
        
        prompt = prompts.get(component, f"Analyze {card_name} for {component}")
        
        # Simulate GPU-accelerated inference
        # In reality, you'd call your LLM here with the prompt
        return f"[GPU-Generated Analysis for {component}]\n\n{prompt}\n\n[Detailed analysis would be generated here using your 8B model on RTX 3070]"
    
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
                        'model_size': '8B',
                        'inference_backend': 'gpu_optimized'
                    }
                }
            }
            
            response = requests.post(
                f"{self.server_url}/api/swarm/submit_results",
                json=payload,
                timeout=60
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
        logger.info(f"Starting desktop worker: {self.worker_id}")
        
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
                    time.sleep(30)
                    continue
                
                # Process tasks
                for task in tasks:
                    start_time = time.time()
                    
                    logger.info(f"Processing task {task['task_id']} for card {task['card_name']}")
                    
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
                        logger.info(f"Completed task {task['task_id']} in {execution_time:.2f}s")
                    else:
                        logger.error(f"Failed to submit task {task['task_id']}")
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("Desktop worker shutting down")

if __name__ == "__main__":
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    worker = DesktopWorker(server_url)
    worker.run()
