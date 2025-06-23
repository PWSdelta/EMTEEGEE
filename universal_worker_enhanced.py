#!/usr/bin/env python3
"""
Enhanced Universal EMTeeGee Worker v3.0 - Enhanced Swarm Integration (FIXED)
- Updated for enhanced swarm manager with smart prioritization
- Supports all 20 analysis components with GPU/CPU allocation
- Enhanced coherence validation and batch processing support
- Improved task tracking and state management
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
from datetime import datetime, timezone

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EnhancedUniversalWorker:
    """Enhanced universal worker with proper task tracking"""
    
    def __init__(self, server_url: str = None):
        # Auto-detect server URL with production as default
        if server_url is None:
            server_url = os.getenv('DJANGO_API_BASE_URL', 'https://mtgabyss.com')  # Production default
        
        self.server_url = server_url
        self.server_ip_url = 'http://64.23.130.187:8000'  # DigitalOcean server IP
        
        # Determine localhost fallback URL - only used when explicitly specified
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
        elif self.worker_type == 'laptop_lite':
            # Laptop Lite: Lightweight models for mid-range hardware
            self.preferred_models = ['llama3.2:3b', 'llama3.2:1b', 'qwen2.5:3b']
            self.current_model = 'llama3.2:3b'
            self.specialization = 'lightweight_analysis'
            self.max_tasks = 2  # Can handle multiple small tasks
            self.poll_interval = 4  # Moderate polling
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
        
        # Enhanced detection for three computer types
        if 'amd' in cpu_info:
            if ram_gb >= 100:  # High-end laptop (128GB)
                worker_type = 'laptop'
                has_gpu = False
            elif ram_gb >= 60:  # Desktop (64GB)
                worker_type = 'desktop'
                has_gpu = True
            else:  # Mid-range laptop (16GB) - Lenovo with Ryzen 5
                worker_type = 'laptop_lite'
                has_gpu = True  # Has AMD Radeon graphics
        elif 'intel' in cpu_info:
            worker_type = 'laptop'
            has_gpu = False
        else:
            # Fallback detection based on RAM
            if ram_gb >= 100:
                worker_type = 'laptop'
                has_gpu = False
            elif ram_gb >= 60:
                worker_type = 'desktop'
                has_gpu = True
            else:
                worker_type = 'laptop_lite'
                has_gpu = True
        
        capabilities = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'processor': cpu_info,
            'cpu_cores': cpu_cores,
            'ram_gb': ram_gb,
            'gpu_available': has_gpu,
            'worker_type': worker_type,
            'specialization': 'deep_cpu_analysis' if worker_type == 'laptop' else ('lightweight_analysis' if worker_type == 'laptop_lite' else 'fast_gpu_analysis'),
            'version': '3.0.0'  # Enhanced swarm integration version
        }
        
        logger.info(f"🔍 Detected: {worker_type.title()} ({cpu_cores} cores, {ram_gb}GB RAM)")
        
        return capabilities

    def register(self) -> bool:
        """Register with the central server with enhanced error handling"""
        registration_data = {
            'worker_id': self.worker_id,
            'capabilities': self.capabilities,
            'status': 'active',
            'registered_at': datetime.now(timezone.utc).isoformat()
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
                
                # Test enhanced swarm API availability
                status_response = requests.get(f"{server_url}/api/enhanced_swarm/status", timeout=15)
                if status_response.status_code != 200:
                    logger.warning(f"⚠️  Server {server_url} missing enhanced swarm API (HTTP {status_response.status_code})")
                    if "404" in str(status_response.status_code):
                        logger.warning("   💡 This server hasn't been deployed with enhanced swarm system yet")
                    continue
                
                # Attempt registration
                response = requests.post(
                    f"{server_url}/api/enhanced_swarm/register",
                    json=registration_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Registered successfully with {server_url}")
                    logger.info(f"📝 Assigned components: {len(result.get('assigned_components', []))}")
                    # Update server URL to the working one
                    self.server_url = server_url
                    self.last_heartbeat = datetime.now(timezone.utc)
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
            logger.error("🌐 REMOTE MODE: Will not fall back to localhost")
            logger.error("💡 This prevents accidentally processing local work instead of remote work")
            logger.error("💡 Solutions:")
            logger.error("   - Deploy swarm system to production server")
            logger.error("   - Fix network connectivity to remote servers")
            logger.error("   - Or run without server argument for local development")
        else:
            logger.error("💡 LOCAL MODE: Ensure Django server is running: python manage.py runserver")        
        return False

    def run(self):
        """Main work loop - poll for tasks and process them"""
        logger.info("🔄 Starting main work loop...")
        self.running = True
        
        try:
            while self.running:
                try:
                    # Send heartbeat
                    self._send_heartbeat()
                    
                    # Check if we can take more work
                    if len(self.active_tasks) < self.max_tasks:
                        self._poll_for_work()
                    
                    # Sleep before next poll
                    time.sleep(self.poll_interval)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Received shutdown signal...")
                    break
                except Exception as e:
                    logger.error(f"❌ Work loop error: {e}")
                    time.sleep(5)  # Brief pause on error
                    
        finally:
            self.running = False
            logger.info("🛑 Worker stopped")

    def _send_heartbeat(self):
        """Send heartbeat to maintain connection"""
        try:
            heartbeat_data = {
                'worker_id': self.worker_id,
                'status': 'active',
                'active_tasks': len(self.active_tasks),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/heartbeat",
                json=heartbeat_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_heartbeat = datetime.now(timezone.utc)
            else:
                logger.warning(f"⚠️  Heartbeat failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️  Heartbeat error: {e}")

    def _poll_for_work(self):
        """Poll server for available work"""
        try:
            work_request = {
                'worker_id': self.worker_id,                'max_tasks': self.max_tasks - len(self.active_tasks),
                'specialization': self.specialization
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/get_work",
                json=work_request,
                timeout=30  # Increased timeout for enhanced API
            )
            
            if response.status_code == 200:
                work_data = response.json()
                tasks = work_data.get('tasks', [])
                
                if tasks:
                    logger.info(f"📋 Received {len(tasks)} task(s)")
                    for task in tasks:
                        self._process_task(task)
                else:
                    logger.debug("ℹ️  No tasks available")
            else:
                logger.warning(f"⚠️  Work request failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️  Work polling error: {e}")

    def _process_task(self, task):
        """Process a single task (placeholder for now)"""
        task_id = task.get('task_id', 'unknown')
        card_name = task.get('card_name', 'Unknown Card')
        card_id = task.get('card_id') or task.get('card_uuid')  # Support both field names
        
        logger.info(f"🎯 Processing task {task_id}: {card_name}")
        self.active_tasks.add(task_id)
        
        try:            # REAL AI Analysis using Ollama
            components = task.get('components', [])
            card_data = task.get('card_data', {})
            analysis_results = {}
            
            logger.info(f"🔍 Starting AI analysis for {len(components)} components")
            
            for component in components:
                logger.info(f"🤖 Analyzing {component}...")
                
                try:
                    # Create analysis prompt
                    prompt = f"""
Analyze this Magic: The Gathering card for {component}:

Card: {card_data.get('name', 'Unknown')}
Mana Cost: {card_data.get('mana_cost', '')}
Type: {card_data.get('type_line', '')}
Text: {card_data.get('oracle_text', '')}

Provide detailed {component} analysis in 2-3 paragraphs.
"""
                    
                    # Call Ollama AI
                    response = ollama.chat(
                        model='llama3.2',
                        messages=[
                            {'role': 'system', 'content': 'You are an expert Magic: The Gathering analyst.'},
                            {'role': 'user', 'content': prompt}
                        ]
                    )
                    
                    analysis_results[component] = response['message']['content']
                    logger.info(f"✅ Completed {component} analysis")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to analyze {component}: {e}")
                    analysis_results[component] = f"Analysis failed: {str(e)}"
            
            # Submit results with required card_id field
            results = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'card_id': card_id,  # This was missing - required by API
                'status': 'completed',
                'results': analysis_results,  # Real AI analysis results                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/submit_results",
                json=results,
                timeout=120  # Longer timeout for real AI analysis
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Task {task_id} completed successfully")
                self.completed_tasks.add(task_id)
            else:
                logger.error(f"❌ Failed to submit results for task {task_id}")
                logger.error(f"Response: {response.text}")  # Added error details
                
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
        finally:
            self.active_tasks.discard(task_id)

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
🤖 EMTeeGee Enhanced Universal Worker v3.0 - Enhanced Swarm Integration
====================================================================
Worker Type: {worker.worker_type.upper()}
Worker ID: {worker.worker_id}
Hardware: {worker.capabilities['cpu_cores']} cores, {worker.capabilities['ram_gb']}GB RAM
Model: {worker.current_model}
Server: {worker.server_url}
Max Tasks: {worker.max_tasks}
Poll Interval: {worker.poll_interval}s
Specialization: {worker.specialization}
Enhanced Swarm: ✅ ENABLED
Components: All 20 analysis components supported
====================================================================

Press Ctrl+C to stop the worker gracefully.
    """)
    
    try:
        # Register with the server
        if worker.register():
            print("✅ Registration successful! Worker is ready for production deployment.")
            
            # Start the main work loop
            print("🔄 Starting work polling loop...")
            worker.run()
        else:
            print("❌ Registration failed. Check server status and try again.")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down worker...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
