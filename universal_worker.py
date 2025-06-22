#!/usr/bin/env python3
"""
Universal EMTeeGee Worker
Automatically detects hardware and configures for optimal performance
- Desktop: GPU models (qwen2.5:7b) for fast processing
- Laptop: Large CPU models (mixtral:8x7b) for deep analysis
"""

import json
import time
import requests
import socket
import platform
import psutil
import multiprocessing
import ollama
import os
import sys
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalWorker:
    """Universal worker that adapts to hardware capabilities"""
    
    def __init__(self, server_url: str = None):
        # Auto-detect server URL
        if server_url is None:
            server_url = os.getenv('DJANGO_API_BASE_URL', 'https://emteegee.tcgplex.com')
        
        self.server_url = server_url
        self.hostname = socket.gethostname()
        self.capabilities = self._detect_capabilities()
        self.worker_type = self.capabilities['worker_type']
        self.worker_id = f"{self.worker_type}-{self.hostname}"
        self.running = False
        
        # Configure models based on hardware
        if self.worker_type == 'desktop':
            self.preferred_models = ['qwen2.5:7b', 'llama3.2:3b']
            self.current_model = 'qwen2.5:7b'
            self.specialization = 'fast_gpu_analysis'
            self.max_tasks = 3  # Can handle more concurrent tasks
        else:  # laptop
            self.preferred_models = ['mixtral:8x7b', 'llama3.3:70b']
            self.current_model = 'mixtral:8x7b'
            self.specialization = 'deep_cpu_analysis'
            self.max_tasks = 1  # Fewer but deeper tasks
        
        logger.info(f"🤖 Initialized {self.worker_type} worker: {self.worker_id}")
        logger.info(f"🎯 Using model: {self.current_model}")
        logger.info(f"🌐 Server: {self.server_url}")
        
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Auto-detect hardware and determine worker type based on CPU"""
        ram_gb = round(psutil.virtual_memory().total / (1024**3))
        cpu_cores = psutil.cpu_count()
        cpu_info = platform.processor().lower()
        
        # Reliable detection: AMD = Desktop, Intel = Laptop
        if 'amd' in cpu_info:
            worker_type = 'desktop'
            has_gpu = True
        elif 'intel' in cpu_info:
            worker_type = 'laptop'
            has_gpu = False
        else:
            # Fallback if neither AMD nor Intel detected clearly
            logger.warning(f"⚠️  Unknown CPU type: {cpu_info}, defaulting to desktop")
            worker_type = 'desktop'
            has_gpu = True
        
        capabilities = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'processor': cpu_info,
            'cpu_cores': cpu_cores,
            'ram_gb': ram_gb,
            'gpu_available': has_gpu,
            'worker_type': worker_type,
            'specialization': 'deep_cpu_analysis' if worker_type == 'laptop' else 'fast_gpu_analysis'
        }
        
        logger.info(f"🔍 Detected: {worker_type.title()} ({cpu_info[:50]})")
        
        return capabilities
    
    def _test_ollama_connection(self) -> bool:
        """Test Ollama connection and model availability"""
        try:
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            
            # Check if any preferred model is available
            model_available = any(model in available_models for model in self.preferred_models)
            if not model_available:
                logger.warning(f"⚠️  Preferred models {self.preferred_models} not found")
                logger.info(f"Available models: {available_models}")
                # Use first available model as fallback
                if available_models:
                    self.current_model = available_models[0]
                    logger.info(f"🔄 Using fallback model: {self.current_model}")
            else:
                # Use the first available preferred model
                for model in self.preferred_models:
                    if model in available_models:
                        self.current_model = model
                        break
            
            logger.info(f"✅ Ollama connection successful - using {self.current_model}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
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
                logger.info(f"✅ Registered successfully: {result}")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False
    
    def get_work(self) -> List[Dict[str, Any]]:
        """Request work from the server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/swarm/get_work",
                json={
                    'worker_id': self.worker_id,
                    'max_tasks': self.max_tasks
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('tasks', [])
            else:
                logger.error(f"❌ Work request failed: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Work request error: {e}")
            return []
    
    def generate_analysis(self, card_data: Dict, components: List[str]) -> Dict[str, str]:
        """Generate analysis using appropriate model for hardware"""
        results = {}
        
        for component in components:
            try:
                prompt = self._create_prompt(card_data, component)
                
                # Configure generation based on worker type
                if self.worker_type == 'desktop':
                    # Fast, efficient analysis for desktop
                    options = {
                        "temperature": 0.7,
                        "num_predict": 200,  # Shorter responses
                        "top_p": 0.9
                    }
                else:
                    # Deep, detailed analysis for laptop
                    options = {
                        "temperature": 0.8,
                        "num_predict": 400,  # Longer, more detailed responses
                        "top_p": 0.95
                    }
                
                response = ollama.generate(
                    model=self.current_model,
                    prompt=prompt,
                    options=options
                )
                
                results[component] = response.get('response', 'No response generated')
                logger.info(f"✅ Generated {component} analysis for {card_data.get('name', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"❌ Analysis failed for {component}: {e}")
                results[component] = f"Analysis failed: {str(e)}"
        
        return results
    
    def _create_prompt(self, card_data: Dict, component: str) -> str:
        """Create analysis prompt based on component and worker type"""
        card_name = card_data.get('name', 'Unknown')
        mana_cost = card_data.get('mana_cost', 'N/A')
        type_line = card_data.get('type_line', 'N/A')
        oracle_text = card_data.get('oracle_text', 'N/A')
        
        base_info = f"""Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}"""
        
        if component == 'play_tips':
            if self.worker_type == 'desktop':
                # Quick, actionable tips for desktop
                return f"""{base_info}

Provide 3 quick gameplay tips for this Magic card. Be concise and practical:
1. When to play it
2. Best synergies  
3. Key timing

Keep responses focused and under 150 words."""
            else:
                # Deep analysis for laptop
                return f"""{base_info}

Provide comprehensive gameplay analysis for this Magic card:
1. Detailed play patterns and timing considerations
2. Synergy analysis with common deck archetypes
3. Meta positioning and competitive viability
4. Advanced strategic applications
5. Common mistakes to avoid

Provide thorough analysis with examples and reasoning."""
        
        elif component == 'deck_building':
            if self.worker_type == 'desktop':
                return f"""{base_info}

Quick deck building advice for this card:
1. What decks want this card
2. Key supporting cards
3. Format recommendations

Keep concise and practical."""
            else:
                return f"""{base_info}

Comprehensive deck building analysis:
1. Detailed archetype fit analysis
2. Extensive synergy breakdown with specific cards
3. Format-by-format evaluation
4. Meta considerations and positioning
5. Build-around potential and supporting strategies

Provide in-depth analysis with multiple examples."""
        
        # Default prompt
        return f"""{base_info}

Analyze this Magic card for {component}. Provide practical insights and recommendations."""
    
    def submit_results(self, task_id: str, card_id: str, results: Dict[str, str]) -> bool:
        """Submit analysis results to the server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/swarm/submit_results",
                json={
                    'worker_id': self.worker_id,
                    'task_id': task_id,
                    'card_id': card_id,
                    'results': results,
                    'worker_type': self.worker_type,
                    'model_used': self.current_model
                },
                timeout=60
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Submitted results for task {task_id}")
                return True
            else:
                logger.error(f"❌ Result submission failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Result submission error: {e}")
            return False
    
    def process_task(self, task: Dict[str, Any]) -> bool:
        """Process a single analysis task"""
        try:
            task_id = task.get('task_id', 'unknown')
            card_data = task.get('card_data', {})
            components = task.get('components', [])
            
            card_name = card_data.get('name', 'Unknown')
            logger.info(f"🔄 Processing {self.worker_type} analysis: {card_name}")
            
            # Generate analysis
            results = self.generate_analysis(card_data, components)
            
            # Submit results
            return self.submit_results(task_id, card_data.get('_id'), results)
            
        except Exception as e:
            logger.error(f"❌ Task processing error: {e}")
            return False
    
    def run(self):
        """Main worker loop"""
        logger.info(f"🚀 Starting {self.worker_type} worker with {self.current_model}")
        
        # Test Ollama connection
        if not self._test_ollama_connection():
            logger.error("❌ Cannot connect to Ollama, exiting")
            return
        
        # Register with server
        if not self.register():
            logger.error("❌ Failed to register, exiting")
            return
        
        self.running = True
        consecutive_empty_polls = 0
        
        while self.running:
            try:
                # Get work
                tasks = self.get_work()
                
                if tasks:
                    consecutive_empty_polls = 0
                    logger.info(f"📋 Received {len(tasks)} task(s)")
                    
                    # Process tasks
                    for task in tasks:
                        if not self.running:
                            break
                        self.process_task(task)
                else:
                    consecutive_empty_polls += 1
                    if consecutive_empty_polls % 10 == 1:  # Log every 10th empty poll
                        logger.info("⏳ No work available, waiting...")
                    time.sleep(5)  # Wait before next poll
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Worker loop error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("👋 Worker stopped")

def main():
    """Main entry point"""
    # Check for server URL argument
    server_url = None
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    # Create and run worker
    worker = UniversalWorker(server_url)
    
    print(f"""
🤖 EMTeeGee Universal Worker
==========================================
Worker Type: {worker.worker_type.upper()}
Hardware: {worker.capabilities['cpu_cores']} cores, {worker.capabilities['ram_gb']}GB RAM
Model: {worker.current_model}
Server: {worker.server_url}
Specialization: {worker.specialization}
==========================================
    """)
    
    try:
        worker.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down worker...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
