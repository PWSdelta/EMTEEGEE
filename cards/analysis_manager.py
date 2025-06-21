"""
MongoDB analysis manager for handling card analysis components.
Implements the "superdoc" approach where analysis data is embedded in card documents.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from django.conf import settings

from .ollama_client import OllamaClient, ALL_COMPONENT_TYPES, COMPONENT_MODEL_MAP

logger = logging.getLogger(__name__)

# Model emoji mapping for logging
MODEL_EMOJIS = {
    'llama3.2:latest': '⚡',
    'llama3.1:latest': '⚖️',
    'qwen2.5:7b-instruct-q4_0': '🚀',
    'mistral:7b': '🎯'
}

# MongoDB field constants
ANALYSIS_FULLY_ANALYZED = "analysis.fully_analyzed"
ANALYSIS_LAST_UPDATED = "analysis.last_updated"
ANALYSIS_COMPONENT_COUNT = "analysis.component_count"
ANALYSIS_COMPLETED_AT = "analysis.analysis_completed_at"

class CardAnalysisManager:
    """Manages card analysis operations in MongoDB."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.cards_collection = None
        self.ollama_client = OllamaClient()
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection."""
        try:
            mongodb_settings = settings.MONGODB_SETTINGS
            
            if mongodb_settings['username'] and mongodb_settings['password']:
                self.client = MongoClient(
                    host=mongodb_settings['host'],
                    username=mongodb_settings['username'],
                    password=mongodb_settings['password'],
                    authSource=mongodb_settings['auth_source']
                )
            else:
                self.client = MongoClient(mongodb_settings['host'])
            
            self.db = self.client[mongodb_settings['db_name']]
            self.cards_collection = self.db['cards']
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_card_by_uuid(self, uuid: str) -> Optional[Dict]:
        """Get a card document by UUID."""
        try:
            return self.cards_collection.find_one({"uuid": uuid})
        except PyMongoError as e:
            logger.error(f"Failed to get card {uuid}: {e}")
            return None
    
    def get_cards_for_analysis(self, limit: int = 100) -> List[Dict]:
        """Get cards that need analysis (not fully analyzed)."""
        try:
            query = {
                "$or": [
                    {ANALYSIS_FULLY_ANALYZED: {"$ne": True}},
                    {"analysis": {"$exists": False}}
                ]
            }
            
            return list(self.cards_collection.find(query).limit(limit))
            
        except PyMongoError as e:
            logger.error(f"Failed to get cards for analysis: {e}")
            return []
    
    def get_analysis_progress(self) -> Dict[str, Any]:
        """Get overall analysis progress statistics."""
        try:
            total_cards = self.cards_collection.count_documents({})
            fully_analyzed = self.cards_collection.count_documents({
                ANALYSIS_FULLY_ANALYZED: True
            })
            
            in_progress = self.cards_collection.count_documents({
                ANALYSIS_COMPONENT_COUNT: {"$gt": 0, "$lt": 20}
            })
            
            return {
                "total_cards": total_cards,
                "fully_analyzed": fully_analyzed,
                "in_progress": in_progress,
                "not_started": total_cards - fully_analyzed - in_progress,
                "completion_percentage": (fully_analyzed / total_cards * 100) if total_cards > 0 else 0
            }
            
        except PyMongoError as e:
            logger.error(f"Failed to get analysis progress: {e}")
            return {}
    
    def initialize_card_analysis(self, uuid: str) -> bool:
        """Initialize analysis structure for a card."""
        try:
            update_result = self.cards_collection.update_one(
                {"uuid": uuid},
                {
                    "$set": {
                        "analysis": {
                            "fully_analyzed": False,
                            "component_count": 0,
                            "analysis_started_at": datetime.now(timezone.utc).isoformat(),
                            "analysis_completed_at": None,
                            "last_updated": datetime.now(timezone.utc).isoformat(),
                            "components": {}
                        }
                    }
                }
            )
            
            return update_result.modified_count > 0
            
        except PyMongoError as e:
            logger.error(f"Failed to initialize analysis for card {uuid}: {e}")
            return False
    
    def add_component(self, uuid: str, component_type: str, component_data: Dict) -> bool:
        """Add a single analysis component to a card."""
        if component_type not in ALL_COMPONENT_TYPES:
            logger.error(f"Invalid component type: {component_type}")
            return False
        
        try:
            # Ensure analysis structure exists
            card = self.get_card_by_uuid(uuid)
            if not card:
                logger.error(f"Card not found: {uuid}")
                return False
            
            if "analysis" not in card:
                self.initialize_card_analysis(uuid)
            
            # Add the component
            update_data = {
                f"analysis.components.{component_type}": component_data,
                ANALYSIS_LAST_UPDATED: datetime.now(timezone.utc).isoformat()
            }
            
            result = self.cards_collection.update_one(
                {"uuid": uuid},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Update component count and fully_analyzed status
                self._update_analysis_status(uuid)
                  # Log successful component addition with word count
                word_count = component_data.get('word_count', 0)
                model_used = component_data.get('model_used', 'unknown')
                model_emoji = MODEL_EMOJIS.get(model_used, '🤖')
                logger.info(f"✅ {component_type} complete! ({word_count}w) {model_emoji}")
                return True
            
            return False
            
        except PyMongoError as e:
            logger.error(f"Failed to add component {component_type} to card {uuid}: {e}")
            return False
    
    def generate_component(self, uuid: str, component_type: str) -> bool:
        """Generate a single component using Ollama."""
        if not self.ollama_client.is_available():
            logger.error("Ollama service is not available")
            return False        
        card = self.get_card_by_uuid(uuid)
        if not card:
            logger.error(f"Card not found: {uuid}")
            return False        
        card_name = card.get('name', uuid)
        # Get the model that will be used for this component
        from .ollama_client import COMPONENT_MODEL_MAP
        model_name = COMPONENT_MODEL_MAP.get(component_type, 'unknown')
          # Shorter, fun logging
        model_emoji = MODEL_EMOJIS.get(model_name, '🤖')
        
        logger.info(f"{model_emoji} Starting {component_type} for '{card_name}'")
        
        try:
            component_data = self.ollama_client.generate_component(card, component_type)
            
            if component_data:
                return self.add_component(uuid, component_type, component_data)
            else:
                logger.error(f"Failed to generate component {component_type} for {uuid}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating component {component_type} for {uuid}: {e}")
            return False
    
    def generate_all_components(self, uuid: str) -> Dict[str, bool]:
        """Generate all 20 components for a card."""
        results = {}
        
        card = self.get_card_by_uuid(uuid)
        if not card:
            logger.error(f"Card not found: {uuid}")
            return results
        
        card_name = card.get('name', uuid)
        logger.info(f"🚀 Analyzing '{card_name[:25]}{'...' if len(card_name) > 25 else ''}' ({max_workers} workers)")
        
        # Initialize analysis if needed
        if "analysis" not in card:
            self.initialize_card_analysis(uuid)
        
        # Count existing components for progress tracking
        existing_components = card.get("analysis", {}).get("components", {})
        total_components = len(ALL_COMPONENT_TYPES)
        
        # Generate each component
        for i, component_type in enumerate(ALL_COMPONENT_TYPES, 1):            # Skip if component already exists
            if component_type in existing_components:
                logger.info(f"[{i}/{total_components}] {component_type} already exists ✓")
                results[component_type] = True
                continue
              # Get model info for logging
            from .ollama_client import COMPONENT_MODEL_MAP
            model_name = COMPONENT_MODEL_MAP.get(component_type, 'unknown')
            model_emoji = MODEL_EMOJIS.get(model_name, '🤖')
            logger.info(f"[{i}/{total_components}] {model_emoji} {component_type}...")
            
            success = self.generate_component(uuid, component_type)
            results[component_type] = success
            
            if success:
                logger.info(f"[{i}/{total_components}] ✅ {component_type} complete!")
            else:
                logger.warning(f"[{i}/{total_components}] ❌ {component_type} failed!")
        
        # Final summary
        successful_count = sum(1 for success in results.values() if success)
        if successful_count == total_components:
            logger.info(f"🎉 '{card_name}' FULLY ANALYZED! All {total_components} components complete!")
        else:
            logger.info(f"📊 '{card_name}' analysis done: {successful_count}/{total_components} components")
        
        return results
    
    def generate_all_components_parallel(self, uuid: str, max_workers: int = 2) -> Dict[str, bool]:
        """Generate all 20 components for a card using parallel processing with model-specific workers."""
        import concurrent.futures
        import threading
        from collections import defaultdict
        
        results = {}
        
        card = self.get_card_by_uuid(uuid)
        if not card:
            logger.error(f"Card not found: {uuid}")
            return results
        
        card_name = card.get('name', uuid)
        logger.info(f"🚀 Parallel analysis starting for '{card_name}' (20 components, {max_workers} workers)")
        
        # Initialize analysis if needed
        if "analysis" not in card:
            self.initialize_card_analysis(uuid)
        
        # Get existing components
        existing_components = card.get("analysis", {}).get("components", {})
        
        # Group components by model for parallel processing
        from .ollama_client import COMPONENT_MODEL_MAP, OLLAMA_MODELS
        model_queues = defaultdict(list)
        
        for component_type in ALL_COMPONENT_TYPES:
            if component_type in existing_components:
                logger.info(f"✓ {component_type} already exists")
                results[component_type] = True
                continue
            
            model = COMPONENT_MODEL_MAP.get(component_type, 'unknown')
            model_queues[model].append(component_type)
        
        # Show the work distribution
        for model, components in model_queues.items():
            if components:
                model_emoji = MODEL_EMOJIS.get(model, '🤖')
                logger.info(f"{model_emoji} {model}: {len(components)} components queued")
        
        def process_component_queue(model, component_queue):
            """Process a queue of components for a specific model."""
            model_results = {}
            model_emoji = MODEL_EMOJIS.get(model, '🤖')
            
            for i, component_type in enumerate(component_queue, 1):
                logger.info(f"{model_emoji} [{i}/{len(component_queue)}] {component_type}...")
                success = self.generate_component(uuid, component_type)
                model_results[component_type] = success
                
                if success:
                    logger.info(f"{model_emoji} ✅ {component_type} done!")
                else:
                    logger.warning(f"{model_emoji} ❌ {component_type} failed!")
            
            return model_results
          # Execute in parallel with ThreadPoolExecutor
        import time
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for each model that has work
            future_to_model = {}
            for i, (model, component_queue) in enumerate(model_queues.items()):
                if component_queue:  # Only submit if there's work to do
                    # Small delay between submissions to prevent overwhelming Ollama
                    if i > 0:
                        time.sleep(0.5)
                    future = executor.submit(process_component_queue, model, component_queue)
                    future_to_model[future] = model
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    model_results = future.result()
                    results.update(model_results)
                    model_emoji = MODEL_EMOJIS.get(model, '🤖')
                    successful = sum(1 for success in model_results.values() if success)
                    logger.info(f"{model_emoji} Model {model} finished: {successful}/{len(model_results)} components")
                except Exception as e:
                    logger.error(f"❌ Model {model} worker failed: {e}")
        
        # Final summary
        successful_count = sum(1 for success in results.values() if success)
        total_components = len(ALL_COMPONENT_TYPES)
        
        if successful_count == total_components:
            logger.info(f"🎉 '{card_name}' FULLY ANALYZED! All {total_components} components complete!")
        else:
            logger.info(f"📊 '{card_name}' parallel analysis done: {successful_count}/{total_components} components")
        
        return results

    def generate_all_components_serial_by_speed(self, uuid: str) -> Dict[str, bool]:
        """Generate all 20 components for a card in serial order by model speed (fast → medium → slow)."""
        from collections import defaultdict
        
        results = {}
        
        card = self.get_card_by_uuid(uuid)
        if not card:
            logger.error(f"Card not found: {uuid}")
            return results
        
        card_name = card.get('name', uuid)
        logger.info(f"🚀 Serial analysis starting for '{card_name[:25]}{'...' if len(card_name) > 25 else ''}' (20 components by speed)")
        
        # Initialize analysis if needed
        if "analysis" not in card:
            self.initialize_card_analysis(uuid)
        
        # Get existing components
        existing_components = card.get("analysis", {}).get("components", {})
        
        # Group components by model speed priority
        from .ollama_client import COMPONENT_MODEL_MAP
          # Model speed tiers (fastest to slowest)
        model_speed_tiers = [
            ('⚡ Fast Models', ['llama3.2:latest']),                      # ~10-30 seconds
            ('⚖️ Medium Models', ['llama3.1:latest', 'mistral:7b']),       # ~30-60 seconds  
            ('🚀 Large Models', ['qwen2.5:7b-instruct-q4_0'])                # ~30-90 seconds
        ]
        
        # Group components by speed tier
        tier_queues = []
        for tier_name, models in model_speed_tiers:
            tier_components = []
            for component_type in ALL_COMPONENT_TYPES:
                if component_type in existing_components:
                    continue
                
                model = COMPONENT_MODEL_MAP.get(component_type, 'unknown')
                if model in models:
                    tier_components.append(component_type)
            
            if tier_components:
                tier_queues.append((tier_name, models[0], tier_components))
        
        # Show the work distribution
        total_remaining = sum(len(components) for _, _, components in tier_queues)
        if total_remaining == 0:
            logger.info("✅ All components already exist!")
            for component_type in ALL_COMPONENT_TYPES:
                results[component_type] = True
            return results
        
        logger.info(f"📋 Processing {total_remaining} components in {len(tier_queues)} speed tiers")
        
        # Process each tier serially
        for tier_name, representative_model, component_queue in tier_queues:
            model_emoji = MODEL_EMOJIS.get(representative_model, '🤖')
            logger.info(f"{model_emoji} {tier_name}: {len(component_queue)} components")
            
            for i, component_type in enumerate(component_queue, 1):
                # Get the actual model for this component
                actual_model = COMPONENT_MODEL_MAP.get(component_type, 'unknown')
                actual_emoji = MODEL_EMOJIS.get(actual_model, '🤖')
                
                logger.info(f"{actual_emoji} [{i}/{len(component_queue)}] {component_type}...")
                success = self.generate_component(uuid, component_type)
                results[component_type] = success
                
                if success:
                    logger.info(f"{actual_emoji} ✅ {component_type} complete!")
                else:
                    logger.warning(f"{actual_emoji} ❌ {component_type} failed!")
            
            logger.info(f"{model_emoji} {tier_name} tier complete!")
        
        # Final summary
        successful_count = sum(1 for success in results.values() if success)
        total_components = len(ALL_COMPONENT_TYPES)
        
        # Add existing components to count
        for component_type in existing_components:
            if component_type not in results:
                results[component_type] = True
                successful_count += 1
        
        if successful_count == total_components:
            logger.info(f"🎉 '{card_name}' FULLY ANALYZED! All {total_components} components complete!")
        else:
            logger.info(f"📊 '{card_name}' serial analysis done: {successful_count}/{total_components} components")
        
        return results
        
    def _update_analysis_status(self, uuid: str):
        """Update the analysis status counters for a card."""
        try:
            card = self.get_card_by_uuid(uuid)
            if not card or "analysis" not in card:
                return
            
            components = card["analysis"].get("components", {})
            component_count = len(components)
            fully_analyzed = component_count >= 20
            
            update_data = {
                ANALYSIS_COMPONENT_COUNT: component_count,
                ANALYSIS_FULLY_ANALYZED: fully_analyzed,
                ANALYSIS_LAST_UPDATED: datetime.now(timezone.utc).isoformat()
            }            
            if fully_analyzed and not card["analysis"].get("analysis_completed_at"):
                update_data[ANALYSIS_COMPLETED_AT] = datetime.now(timezone.utc).isoformat()
                logger.info(f"🎉 '{card.get('name', uuid)}' is now FULLY ANALYZED! All 20 components complete.")
            elif component_count > 0:
                logger.info(f"Progress update for '{card.get('name', uuid)}': {component_count}/20 components complete")
            
            self.cards_collection.update_one(
                {"uuid": uuid},
                {"$set": update_data}
            )
                
        except PyMongoError as e:
            logger.error(f"Failed to update analysis status for {uuid}: {e}")
    
    def get_card_analysis(self, uuid: str) -> Optional[Dict]:
        """Get analysis data for a card."""
        card = self.get_card_by_uuid(uuid)
        if not card:
            return None
        
        return card.get("analysis", {})
    
    def get_component(self, uuid: str, component_type: str) -> Optional[Dict]:
        """Get a specific component for a card."""
        analysis = self.get_card_analysis(uuid)
        if not analysis:
            return None
        
        return analysis.get("components", {}).get(component_type)
    
    def delete_component(self, uuid: str, component_type: str) -> bool:
        """Delete a specific component (for reanalysis)."""
        try:
            result = self.cards_collection.update_one(
                {"uuid": uuid},                {
                    "$unset": {f"analysis.components.{component_type}": ""},
                    "$set": {ANALYSIS_LAST_UPDATED: datetime.now(timezone.utc).isoformat()}
                }
            )
            
            if result.modified_count > 0:
                self._update_analysis_status(uuid)
                return True
            
            return False
            
        except PyMongoError as e:
            logger.error(f"Failed to delete component {component_type} from card {uuid}: {e}")
            return False
    
    def reset_card_analysis(self, uuid: str) -> bool:
        """Reset all analysis for a card."""
        try:
            result = self.cards_collection.update_one(
                {"uuid": uuid},
                {
                    "$unset": {"analysis": ""}
                }
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            logger.error(f"Failed to reset analysis for card {uuid}: {e}")
            return False
    
    def get_cards_by_analysis_status(self, fully_analyzed: bool = None, limit: int = 100) -> List[Dict]:
        """Get cards filtered by analysis status."""
        try:
            if fully_analyzed is None:                # Get all cards
                query = {}
            elif fully_analyzed:
                # Get fully analyzed cards
                query = {ANALYSIS_FULLY_ANALYZED: True}
            else:                # Get cards that need analysis
                query = {
                    "$or": [
                        {ANALYSIS_FULLY_ANALYZED: {"$ne": True}},
                        {"analysis": {"$exists": False}}
                    ]
                }
            
            return list(self.cards_collection.find(query).limit(limit))
            
        except PyMongoError as e:
            logger.error(f"Failed to get cards by analysis status: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

# Global instance for use across the application
analysis_manager = CardAnalysisManager()
