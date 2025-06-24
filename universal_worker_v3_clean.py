#!/usr/bin/env python3
"""
Enhanced Universal EMTeeGee Worker v3.0 - Enhanced Swarm Integration
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
    """Enhanced universal worker v3.0 with enhanced swarm integration"""
    
    def __init__(self, server_url: str = None):
        # Auto-detect server URL with fallback
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
            self.preferred_models = ['llama3.1:8b']
            self.current_model = 'llama3.1:8b'            
            self.specialization = 'fast_gpu_analysis'
            self.max_tasks = 2  # Reduced for better tracking
            self.poll_interval = 3  # Faster polling for GPU worker
        elif self.worker_type == 'laptop_lite':
            # Laptop Lite: Lightweight models for mid-range hardware
            self.preferred_models = ['llama3.2:3b']
            self.current_model = 'llama3.2:3b'
            self.specialization = 'lightweight_analysis'
            self.max_tasks = 2  # Can handle multiple small tasks
            self.poll_interval = 4  # Moderate polling
        else:  # laptop
            self.preferred_models = ['llama3.3:70b', 'llama3.3:70b']
            self.current_model = 'llama3.3:70b'
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
            'specialization': self._get_specialization(worker_type),
            'version': '3.0.0'  # Enhanced swarm integration version
        }
        
        logger.info(f"Detected: {worker_type.title()} ({cpu_cores} cores, {ram_gb}GB RAM)")
        
        return capabilities
    
    def _get_specialization(self, worker_type: str) -> str:
        """Get specialization based on worker type"""
        if worker_type == 'laptop':
            return 'deep_cpu_analysis'
        elif worker_type == 'laptop_lite':
            return 'lightweight_analysis'
        else:
            return 'fast_gpu_analysis'
    def _test_ollama_connection(self) -> bool:
        """Test Ollama connection and model availability"""
        try:
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            
            # Check if any preferred model is available
            model_available = any(model in available_models for model in self.preferred_models)
            
            if not model_available:
                logger.warning(f"Preferred models {self.preferred_models} not found")
                logger.info(f"Available models: {available_models}")
                # Use first available model as fallback
                if available_models:
                    self.current_model = available_models[0]
                    logger.info(f"Using fallback model: {self.current_model}")
                else:
                    logger.error("No models available in Ollama")
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
            logger.error("🚫 REMOTE MODE: Will not fall back to localhost")
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
                'last_heartbeat': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/heartbeat",
                json=heartbeat_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_heartbeat = datetime.now(timezone.utc)
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
                'completed_task_ids': list(self.completed_tasks),  # Exclude completed tasks
                'random_assignment': True  # Explicitly request random assignment, no EDHREC priority
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/get_work",
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
        """Submit analysis results with enhanced tracking for new swarm system"""
        try:
            # Debug: Log what we're about to submit
            logger.info(f"🔍 DEBUG - Preparing submission:")
            logger.info(f"  - worker_id: {self.worker_id}")
            logger.info(f"  - task_id: {task_id}")
            logger.info(f"  - card_id: {card_id}")
            logger.info(f"  - results keys: {list(results.keys()) if results else 'None'}")
            
            if not card_id:
                logger.error(f"❌ Missing card_id for task {task_id}")
                return False
                
            # Format results for the new enhanced swarm manager
            submission_data = {
                'worker_id': self.worker_id,
                'task_id': task_id,
                'card_id': card_id,
                'results': {
                    'components': results,
                    'model_info': {
                        'model_name': self.current_model,
                        'worker_type': self.worker_type,
                        'specialization': self.specialization
                    },
                    'execution_time': 0
                }
            }
            
            # Debug: Log the exact payload
            logger.info(f"🔍 DEBUG - Submission payload keys: {list(submission_data.keys())}")
            logger.info(f"🔍 DEBUG - Results structure: {type(submission_data['results'])}")
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/submit_results",
                json=submission_data,
                timeout=60
            )
            
            if response.status_code == 200:
                # Remove from active tasks and add to completed
                if task_id in self.active_tasks:
                    self.active_tasks.remove(task_id)
                self.completed_tasks.add(task_id)
                
                logger.info(f"✅ Submitted results for task {task_id} (card: {card_id})")
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
            
            # Extract card ID from various possible sources
            card_id = (
                task.get('card_id') or 
                task.get('card_uuid') or 
                card_data.get('uuid') or 
                card_data.get('_id') or
                card_data.get('id')
            )
            
            card_name = card_data.get('name', 'Unknown')
            logger.info(f"🔄 Processing {self.worker_type} analysis: {card_name} (Task: {task_id})")
            # logger.info(f"📝 Components: {', '.join(components)}")
            logger.info(f"🆔 Card ID: {card_id}")
            
            # Generate analysis
            results = self.generate_analysis(card_data, components)
            
            # Validate results
            if not results or all(not v for v in results.values()):
                logger.error(f"❌ No valid analysis generated for {card_name}")
                return False
            
            # Submit results with card_id
            success = self.submit_results(task_id, card_id, results)
            
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
                elif self.worker_type == 'laptop_lite':
                    # Lightweight analysis for laptop lite
                    options = {
                        "temperature": 0.7,
                        "num_predict": 200,  # Shorter responses for efficiency
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
        """Create enhanced analysis prompts for all component types"""
        card_name = card_data.get('name', 'Unknown')
        mana_cost = card_data.get('manaCost', card_data.get('mana_cost', 'N/A'))
        type_line = card_data.get('type', card_data.get('type_line', 'N/A'))
        oracle_text = card_data.get('text', card_data.get('oracle_text', 'N/A'))
        power = card_data.get('power', '')
        toughness = card_data.get('toughness', '')
        
        # Build comprehensive card info
        base_info = f"""Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}"""
        
        if power and toughness:
            base_info += f"\nPower/Toughness: {power}/{toughness}"
        
        base_info += f"\nText: {oracle_text}"
        
        # Enhanced component-specific prompts matching the new swarm manager structure
        component_prompts = {
            # GPU_COMPONENTS (Fast, efficient analysis)
            'play_tips': f"""{base_info}

Provide practical gameplay tips for [[{card_name}]]:
1. Optimal timing and situations for play
2. Best synergies and combinations  
3. Key strategic considerations
4. Common mistakes to avoid

Be concise and actionable.""",

            'mulligan_considerations': f"""{base_info}

Analyze mulligan decisions for [[{card_name}]]:
1. When to keep hands with this card
2. When to mulligan it away
3. Hand quality evaluation with this card
4. Opening hand priorities

Focus on practical decision-making.""",

            'rules_clarifications': f"""{base_info}

Provide rules analysis for [[{card_name}]]:
1. Complex rules interactions and timing
2. Common misconceptions  
3. Edge cases and rulings
4. Layer system interactions if applicable

Be precise and comprehensive.""",

            'combo_suggestions': f"""{base_info}

Analyze combo potential for [[{card_name}]]:
1. Direct combo pieces and interactions
2. Synergistic packages and engines
3. Win condition setups
4. Casual and competitive combinations

Include specific card recommendations.""",

            'format_analysis': f"""{base_info}

Evaluate [[{card_name}]] across formats:
1. Standard viability and applications
2. Modern/Pioneer positioning
3. Legacy/Vintage considerations  
4. Commander/EDH role
5. Limited/Draft value

Provide format-specific insights.""",

            'synergy_analysis': f"""{base_info}

Analyze synergies for [[{card_name}]]:
1. Cards that work well with this
2. Archetype synergies and fit
3. Anti-synergies to avoid
4. Deck building considerations

Include specific card and strategy examples.""",

            'competitive_analysis': f"""{base_info}

Assess competitive viability of [[{card_name}]]:
1. Current meta positioning
2. Tournament results and trends
3. Competitive advantages/weaknesses
4. Future competitive potential

Be analytical and data-driven.""",

            'tactical_analysis': f"""{base_info}

Provide tactical guidance for [[{card_name}]]:
1. Optimal timing and sequencing
2. Key interactions and decision points
3. Play patterns and lines
4. Situational considerations

Focus on in-game tactics.""",

            # CPU_HEAVY_COMPONENTS (Deep, detailed analysis)
            'thematic_analysis': f"""{base_info}

Analyze the thematic elements of [[{card_name}]]:
1. Lore and story connections
2. Flavor text significance
3. Art and design theme coherence
4. Place in MTG's world-building

Explore narrative and artistic depth.""",

            'historical_context': f"""{base_info}

Provide historical context for [[{card_name}]]:
1. Design evolution and precedents
2. Meta impact when released
3. Power level shifts over time
4. Historical significance in MTG

Include design and competitive history.""",

            'art_flavor_analysis': f"""{base_info}

Analyze the artistic and flavor elements of [[{card_name}]]:
1. Art analysis and visual storytelling
2. Flavor text analysis and meaning
3. Creative design and aesthetic
4. Cultural and artistic references

Focus on creative and artistic elements.""",

            'design_philosophy': f"""{base_info}

Examine the design philosophy of [[{card_name}]]:
1. Design goals and intentions
2. Mechanical innovation and precedent
3. Balance considerations and constraints
4. Design space exploration

Analyze from a design perspective.""",

            'advanced_interactions': f"""{base_info}

Analyze complex interactions for [[{card_name}]]:
1. Complex edge cases and scenarios
2. Layer system interactions
3. Timing and priority issues
4. Judge call scenarios

Cover advanced rules complexity.""",

            'meta_positioning': f"""{base_info}

Analyze meta positioning for [[{card_name}]]:
1. Role in current metagame
2. Matchup considerations
3. Meta shifts that affect it
4. Adaptation potential

Focus on competitive metagame analysis.""",

            # BALANCED_COMPONENTS (Accessible analysis)
            'budget_alternatives': f"""{base_info}

Provide budget analysis for [[{card_name}]]:
1. Budget-friendly alternatives
2. Cost-effective substitutions
3. Budget deck considerations
4. Performance trade-offs

Help players with limited budgets.""",

            'deck_archetypes': f"""{base_info}

Analyze deck archetype fit for [[{card_name}]]:
1. Primary deck types that want this
2. Archetype-specific roles
3. Deck building considerations
4. Alternative inclusions

Cover various competitive archetypes.""",

            'new_player_guide': f"""{base_info}

Create new player guidance for [[{card_name}]]:
1. Basic functionality explanation
2. Good/bad for beginners assessment
3. Learning opportunities
4. Common beginner mistakes

Make it accessible for new players.""",

            'sideboard_guide': f"""{base_info}

Provide sideboard guidance for [[{card_name}]]:
1. Sideboard applications and timing
2. Matchups where it's important
3. Meta-specific considerations
4. Sideboard card interactions

Focus on competitive sideboarding.""",

            'power_level_assessment': f"""{base_info}

Assess the power level of [[{card_name}]]:
1. Overall power rating and justification
2. Comparison to similar cards
3. Power level in different contexts
4. Historical power level perspective

Provide objective power assessment.""",

            'investment_outlook': f"""{base_info}

Analyze investment potential for [[{card_name}]]:
1. Current market position
2. Factors affecting value
3. Long-term outlook
4. Collectibility considerations

Focus on financial and collectible aspects."""
        }

        # Return the appropriate prompt or create a default
        if component in component_prompts:
            return component_prompts[component]
        else:
            # Default prompt for any unspecified components
            return f"""{base_info}

Analyze [[{card_name}]] for {component.replace('_', ' ')}.
Provide detailed insights and practical recommendations.
Be thorough and specific in your analysis."""
    
    def run(self):
        """Enhanced main worker loop with better state management"""
        logger.info(f"🚀 Starting {self.worker_type} worker v3.0 - Enhanced Swarm Integration")
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

def run_worker_loop(self):
    """Enhanced worker loop with failed task cleanup"""
    try:
        iteration = 0
        failed_task_cleanup_counter = 0
        
        while True:
            iteration += 1
            failed_task_cleanup_counter += 1
            
            # Send heartbeat
            if not self.send_heartbeat():
                logger.warning("⚠️  Heartbeat failed - continuing")
            
            # Every 10 iterations, clean up failed tasks
            if failed_task_cleanup_counter >= 10:
                self.cleanup_failed_tasks()
                failed_task_cleanup_counter = 0
            
            # Check if we can take more work
            if len(self.active_tasks) < self.max_tasks:
                new_tasks = self.get_work()
                
                for task in new_tasks:
                    if self.process_task(task):
                        logger.info(f"✅ Task completed successfully")
                    else:
                        logger.error(f"❌ Task processing failed")
                        # Remove failed task from active queue
                        task_id = task.get('task_id')
                        if task_id in self.active_tasks:
                            self.active_tasks.remove(task_id)
                            logger.info(f"🧹 Removed failed task {task_id} from active queue")
            else:
                logger.info(f"🔄 Worker at capacity - Active: {len(self.active_tasks)}/{self.max_tasks}")
            
            time.sleep(self.poll_interval)
            
    except KeyboardInterrupt:
        logger.info("👋 Worker shutdown requested")
    except Exception as e:
        logger.error(f"💥 Worker loop error: {e}")

def cleanup_failed_tasks(self):
    """Remove tasks that have been active too long (likely failed)"""
    if not hasattr(self, 'task_start_times'):
        self.task_start_times = {}
    
    current_time = time.time()
    stale_tasks = []
    
    for task_id in list(self.active_tasks):
        # If task has been active for more than 30 minutes, consider it stale
        start_time = self.task_start_times.get(task_id, current_time)
        if current_time - start_time > 1800:  # 30 minutes
            stale_tasks.append(task_id)
    
    for task_id in stale_tasks:
        self.active_tasks.remove(task_id)
        if task_id in self.task_start_times:
            del self.task_start_times[task_id]
        logger.warning(f"🧹 Cleaned up stale task: {task_id}")
    
    if stale_tasks:
        logger.info(f"🧹 Cleaned up {len(stale_tasks)} stale tasks")

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
        worker.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down worker...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
