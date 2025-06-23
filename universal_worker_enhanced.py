#!/usr/bin/env python3
"""
Enhanced Universal EMTeeGee Worker
- Fixed duplicate card processing issue
- Improved task tracking and state management
- Enhanced error handling and recovery
- Better logging and monitoring
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
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EnhancedUniversalWorker:
    """Enhanced universal worker with proper task tracking"""
    
    def __init__(self, server_url: str = None):        # Auto-detect server URL with fallback
        if server_url is None:
            server_url = os.getenv('DJANGO_API_BASE_URL', 'https://mtgabyss.com')
        
        self.server_url = server_url
        self.server_ip_url = 'http://64.23.130.187:8000'  # DigitalOcean server IP
        
        # Determine localhost fallback URL based on common Django ports
        if 'localhost:8001' in server_url or '127.0.0.1:8001' in server_url:
            self.fallback_url = 'http://localhost:8001'
        else:
            self.fallback_url = 'http://localhost:8000'
        self.hostname = socket.gethostname()
        self.capabilities = self._detect_capabilities()
        self.worker_type = self.capabilities['worker_type']
        self.worker_id = f"{self.worker_type}-{self.hostname}"
        self.running = False
        
        # Task tracking
        self.active_tasks = set()  # Track tasks currently being processed
        self.completed_tasks = set()  # Track completed tasks to avoid duplicates
        self.last_heartbeat = None
        
        # Configure models based on hardware
        if self.worker_type == 'desktop':
            self.preferred_models = ['qwen2.5:7b', 'llama3.2:3b']
            self.current_model = 'qwen2.5:7b'
            self.specialization = 'fast_gpu_analysis'
            self.max_tasks = 2  # Reduced for better tracking
            self.poll_interval = 3  # Faster polling for GPU worker
        else:  # laptop
            self.preferred_models = ['mixtral:8x7b', 'llama3.3:70b']
            self.current_model = 'mixtral:8x7b'
            self.specialization = 'deep_cpu_analysis'
            self.max_tasks = 1  # Single task for deep analysis
            self.poll_interval = 5  # Slower polling for CPU worker
        
        logger.info(f"🤖 Initialized {self.worker_type} worker: {self.worker_id}")
        logger.info(f"🎯 Using model: {self.current_model}")
        logger.info(f"🌐 Server: {self.server_url}")
        logger.info(f"⚙️  Max concurrent tasks: {self.max_tasks}")
        
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Auto-detect hardware and determine worker type"""
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
            # Fallback detection based on RAM
            if ram_gb >= 100:  # Laptop has 128GB
                worker_type = 'laptop'
                has_gpu = False
            else:  # Desktop has 64GB
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
            'specialization': 'deep_cpu_analysis' if worker_type == 'laptop' else 'fast_gpu_analysis',
            'version': '2.0.0'  # Enhanced version
        }
        
        logger.info(f"🔍 Detected: {worker_type.title()} ({cpu_cores} cores, {ram_gb}GB RAM)")
        
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
                    logger.error("❌ No models available in Ollama")
                    return False
            else:
                # Use the first available preferred model
                for model in self.preferred_models:
                    if model in available_models:
                        self.current_model = model
                        break
            
            # Test the model with a simple query
            test_response = ollama.generate(
                model=self.current_model,
                prompt="Test connection. Respond with 'OK'.",
                options={"num_predict": 5}
            )
            
            if test_response.get('response'):
                logger.info(f"✅ Ollama connection successful - using {self.current_model}")
                return True
            else:
                logger.error("❌ Model test failed - no response")
                return False
            
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            return False
    
    def register(self) -> bool:
        """Register with the central server with enhanced error handling"""
        registration_data = {
            'worker_id': self.worker_id,
            'capabilities': self.capabilities,
            'status': 'active',
            'registered_at': datetime.utcnow().isoformat()
        }
        
        # Determine servers to try based on configuration
        if self.server_url == self.fallback_url:
            # If configured for localhost, only try localhost
            servers_to_try = [self.fallback_url]
            logger.info("🏠 Configured for local development mode")
        else:
            # If configured for remote, try remote servers only (NO localhost fallback)
            servers_to_try = [self.server_url, self.server_ip_url]
            logger.info("🌐 Configured for remote/distributed mode")
            logger.info("⚠️  Will NOT fall back to localhost - this prevents accidental local work")
        
        for i, server_url in enumerate(servers_to_try):
            try:
                logger.info(f"🔄 Attempting registration with {server_url} ({i+1}/{len(servers_to_try)})")
                
                # First test basic connectivity
                basic_response = requests.get(f"{server_url}/", timeout=15)
                if basic_response.status_code != 200:
                    logger.warning(f"⚠️  Server {server_url} basic connectivity failed: HTTP {basic_response.status_code}")
                    continue
                
                # Test swarm API availability
                status_response = requests.get(f"{server_url}/api/swarm/status", timeout=15)
                if status_response.status_code != 200:
                    logger.warning(f"⚠️  Server {server_url} missing swarm API (HTTP {status_response.status_code})")
                    if "404" in str(status_response.status_code):
                        logger.warning("   💡 This server hasn't been deployed with swarm system yet")
                    continue
                
                # Attempt registration
                response = requests.post(
                    f"{server_url}/api/swarm/register",
                    json=registration_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Registered successfully with {server_url}")
                    logger.info(f"📝 Assigned components: {len(result.get('assigned_components', []))}")
                    # Update server URL to the working one
                    self.server_url = server_url
                    self.last_heartbeat = datetime.utcnow()
                    return True
                else:
                    logger.warning(f"⚠️  Registration failed: HTTP {response.status_code} - {response.text[:200]}")
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️  Connection refused to {server_url}: {str(e)[:100]}...")
            except requests.exceptions.Timeout as e:
                logger.warning(f"⚠️  Timeout connecting to {server_url}: {str(e)[:100]}...")
            except Exception as e:
                logger.warning(f"⚠️  Registration error with {server_url}: {str(e)[:100]}...")
        
        logger.error("❌ Registration failed on all configured servers")
        if self.server_url != self.fallback_url:
            logger.error("� REMOTE MODE: Will not fall back to localhost")
            logger.error("💡 This prevents accidentally processing local work instead of remote work")
            logger.error("💡 Solutions:")
            logger.error("   - Deploy swarm system to production server")
            logger.error("   - Fix network connectivity to remote servers")
            logger.error("   - Or run without server argument for local development")
        else:
            logger.error("💡 LOCAL MODE: Ensure Django server is running: python manage.py runserver")
        
        return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to maintain worker status"""
        try:
            heartbeat_data = {
                'worker_id': self.worker_id,
                'status': 'active',
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'last_heartbeat': datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/swarm/heartbeat",
                json=heartbeat_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_heartbeat = datetime.utcnow()
                return True
            else:
                logger.warning(f"⚠️  Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Heartbeat error: {e}")
            return False
    
    def get_work(self) -> List[Dict[str, Any]]:
        """Request work from the server with improved task filtering"""
        try:
            # Calculate how many new tasks we can take
            available_slots = self.max_tasks - len(self.active_tasks)
            if available_slots <= 0:
                return []
            
            request_data = {
                'worker_id': self.worker_id,
                'max_tasks': available_slots,
                'worker_type': self.worker_type,
                'specialization': self.specialization,
                'active_task_ids': list(self.active_tasks),  # Exclude tasks we're already working on
                'completed_task_ids': list(self.completed_tasks)  # Exclude completed tasks
            }
            
            response = requests.post(
                f"{self.server_url}/api/swarm/get_work",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tasks = result.get('tasks', [])
                
                # Add tasks to active tracking
                for task in tasks:
                    task_id = task.get('task_id')
                    if task_id:
                        self.active_tasks.add(task_id)
                        logger.info(f"📋 Added task {task_id} to active queue")
                
                return tasks
            else:
                logger.error(f"❌ Work request failed: HTTP {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Work request error: {e}")
            return []
    
    def submit_results(self, task_id: str, card_id: str, results: Dict[str, str]) -> bool:
        """Submit analysis results with enhanced tracking"""
        try:
            submission_data = {
                'worker_id': self.worker_id,
                'task_id': task_id,
                'card_id': card_id,
                'results': results,
                'worker_type': self.worker_type,
                'model_used': self.current_model,
                'completed_at': datetime.utcnow().isoformat(),
                'processing_time': None  # Could add timing metrics
            }
            
            response = requests.post(
                f"{self.server_url}/api/swarm/submit_results",
                json=submission_data,
                timeout=60
            )
            
            if response.status_code == 200:
                # Remove from active tasks and add to completed
                if task_id in self.active_tasks:
                    self.active_tasks.remove(task_id)
                self.completed_tasks.add(task_id)
                
                logger.info(f"✅ Submitted results for task {task_id}")
                logger.info(f"📊 Active: {len(self.active_tasks)}, Completed: {len(self.completed_tasks)}")
                return True
            else:
                logger.error(f"❌ Result submission failed: HTTP {response.status_code} - {response.text[:200]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Result submission error: {e}")
            return False
    
    def process_task(self, task: Dict[str, Any]) -> bool:
        """Process a single analysis task with enhanced error handling"""
        task_id = task.get('task_id', 'unknown')
        start_time = time.time()
        
        try:
            card_data = task.get('card_data', {})
            components = task.get('components', [])
            
            card_name = card_data.get('name', 'Unknown')
            logger.info(f"🔄 Processing {self.worker_type} analysis: {card_name} (Task: {task_id})")
            logger.info(f"📝 Components: {', '.join(components)}")
            
            # Generate analysis
            results = self.generate_analysis(card_data, components)
            
            # Validate results
            if not results or all(not v for v in results.values()):
                logger.error(f"❌ No valid analysis generated for {card_name}")
                return False
            
            # Submit results
            success = self.submit_results(task_id, card_data.get('_id'), results)
            
            processing_time = time.time() - start_time
            logger.info(f"⏱️  Task {task_id} completed in {processing_time:.1f}s")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Task processing error for {task_id}: {e}")
            # Remove from active tasks on error
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            return False
    
    def generate_analysis(self, card_data: Dict, components: List[str]) -> Dict[str, str]:
        """Generate analysis with improved prompts and error handling"""
        results = {}
        card_name = card_data.get('name', 'Unknown')
        
        for component in components:
            try:
                logger.info(f"🧠 Generating {component} for {card_name}")
                
                prompt = self._create_enhanced_prompt(card_data, component)
                
                # Configure generation based on worker type
                if self.worker_type == 'desktop':
                    # Fast, efficient analysis for desktop
                    options = {
                        "temperature": 0.7,
                        "num_predict": 250,  # Balanced length
                        "top_p": 0.9,
                        "repeat_penalty": 1.1
                    }
                else:
                    # Deep, detailed analysis for laptop
                    options = {
                        "temperature": 0.8,
                        "num_predict": 400,  # Longer responses
                        "top_p": 0.95,
                        "repeat_penalty": 1.1
                    }
                
                response = ollama.generate(
                    model=self.current_model,
                    prompt=prompt,
                    options=options
                )
                
                analysis_text = response.get('response', '').strip()
                
                if analysis_text and len(analysis_text) > 10:  # Validate minimum content
                    results[component] = analysis_text
                    logger.info(f"✅ Generated {component} ({len(analysis_text)} chars)")
                else:
                    logger.warning(f"⚠️  Short/empty response for {component}")
                    results[component] = f"Analysis incomplete for {component}"
                
            except Exception as e:
                logger.error(f"❌ Analysis failed for {component}: {e}")
                results[component] = f"Analysis failed: {str(e)}"
        
        return results
    
    def _create_enhanced_prompt(self, card_data: Dict, component: str) -> str:
        """Create enhanced analysis prompts"""
        card_name = card_data.get('name', 'Unknown')
        mana_cost = card_data.get('mana_cost', 'N/A')
        type_line = card_data.get('type_line', 'N/A')
        oracle_text = card_data.get('oracle_text', 'N/A')
        power = card_data.get('power', '')
        toughness = card_data.get('toughness', '')
        
        # Build comprehensive card info
        base_info = f"""Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}"""
        
        if power and toughness:
            base_info += f"\nPower/Toughness: {power}/{toughness}"
        
        base_info += f"\nText: {oracle_text}"
        
        # Component-specific prompts
        prompts = {
            'play_tips': {
                'desktop': f"""{base_info}

Provide 3 essential gameplay tips for this Magic card:
1. Optimal timing and situations for play
2. Best synergies and combinations
3. Key strategic considerations

Be practical and concise (150-200 words).""",
                
                'laptop': f"""{base_info}

Provide comprehensive gameplay analysis:
1. Detailed play patterns and timing windows
2. Synergy analysis with popular archetypes
3. Meta positioning and competitive applications
4. Advanced strategic depth and edge cases
5. Common play mistakes and how to avoid them

Include specific examples and detailed reasoning (300-400 words)."""
            },
            
            'deck_building': {
                'desktop': f"""{base_info}

Quick deck building guide:
1. Primary deck archetypes that want this card
2. Essential supporting cards and synergies
3. Format recommendations and considerations

Focus on actionable advice (150-200 words).""",
                
                'laptop': f"""{base_info}

Comprehensive deck building analysis:
1. Detailed archetype breakdown and fit analysis
2. Extensive synergy mapping with specific card recommendations
3. Format-by-format evaluation and positioning
4. Meta considerations and competitive outlook
5. Build-around potential and deck construction strategies

Provide thorough analysis with multiple examples (300-400 words)."""
            },
            
            'competitive_analysis': {
                'desktop': f"""{base_info}

Tournament viability assessment:
1. Current meta positioning
2. Competitive advantages and weaknesses
3. Format-specific evaluation

Be direct and analytical (150-200 words).""",
                
                'laptop': f"""{base_info}

Deep competitive analysis:
1. Comprehensive meta positioning across formats
2. Tournament performance history and trends
3. Competitive advantages, weaknesses, and applications
4. Matchup analysis against popular strategies
5. Future competitive potential and outlook

Include statistical context and strategic depth (300-400 words)."""
            }
        }
        
        # Get appropriate prompt or create default
        if component in prompts:
            return prompts[component].get(self.worker_type, prompts[component]['desktop'])
        else:
            # Default prompt for unspecified components
            detail_level = "detailed" if self.worker_type == 'laptop' else "concise"
            word_count = "300-400" if self.worker_type == 'laptop' else "150-200"
            
            return f"""{base_info}

Analyze this Magic card for {component.replace('_', ' ')}. Provide {detail_level} insights and practical recommendations.

Target length: {word_count} words."""
    
    def run(self):
        """Enhanced main worker loop with better state management"""
        logger.info(f"🚀 Starting {self.worker_type} worker v2.0")
        logger.info(f"🎯 Model: {self.current_model}")
        logger.info(f"⚙️  Max tasks: {self.max_tasks}, Poll interval: {self.poll_interval}s")
        
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
        last_heartbeat = time.time()
        
        logger.info("✅ Worker started successfully - entering main loop")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Send heartbeat every 30 seconds
                if current_time - last_heartbeat > 30:
                    self.send_heartbeat()
                    last_heartbeat = current_time
                
                # Get work only if we have available slots
                available_slots = self.max_tasks - len(self.active_tasks)
                
                if available_slots > 0:
                    tasks = self.get_work()
                    
                    if tasks:
                        consecutive_empty_polls = 0
                        logger.info(f"📋 Received {len(tasks)} task(s) - Active: {len(self.active_tasks)}")
                        
                        # Process tasks
                        for task in tasks:
                            if not self.running:
                                break
                            self.process_task(task)
                    else:
                        consecutive_empty_polls += 1
                        if consecutive_empty_polls % 20 == 1:  # Log every 20th empty poll
                            logger.info(f"⏳ No work available - Active: {len(self.active_tasks)}, Completed: {len(self.completed_tasks)}")
                else:
                    logger.info(f"🔄 Worker at capacity - Active: {len(self.active_tasks)}/{self.max_tasks}")
                
                # Sleep before next poll
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Worker loop error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info(f"👋 Worker stopped - Completed {len(self.completed_tasks)} tasks")

def main():
    """Main entry point with enhanced argument parsing"""
    # Check for server URL argument
    server_url = None
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
        print(f"Using server URL from argument: {server_url}")
    
    # Create and run worker
    worker = EnhancedUniversalWorker(server_url)
    
    print(f"""
🤖 EMTeeGee Enhanced Universal Worker v2.0
==========================================
Worker Type: {worker.worker_type.upper()}
Worker ID: {worker.worker_id}
Hardware: {worker.capabilities['cpu_cores']} cores, {worker.capabilities['ram_gb']}GB RAM
Model: {worker.current_model}
Server: {worker.server_url}
Max Tasks: {worker.max_tasks}
Poll Interval: {worker.poll_interval}s
Specialization: {worker.specialization}
==========================================

Press Ctrl+C to stop the worker gracefully.
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
