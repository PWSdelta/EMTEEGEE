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
                logger.info(f"✓ Added {component_type} component ({word_count} words, {model_used})")
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
        logger.info(f"Generating {component_type} for '{card_name}' using {model_name}")
        
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
        logger.info(f"Starting full analysis for '{card_name}' - generating all 20 components")
        
        # Initialize analysis if needed
        if "analysis" not in card:
            self.initialize_card_analysis(uuid)
        
        # Count existing components for progress tracking
        existing_components = card.get("analysis", {}).get("components", {})
        total_components = len(ALL_COMPONENT_TYPES)
        
        # Generate each component
        for i, component_type in enumerate(ALL_COMPONENT_TYPES, 1):
            # Skip if component already exists
            if component_type in existing_components:
                logger.info(f"[{i}/{total_components}] Component {component_type} already exists for '{card_name}' ✓")
                results[component_type] = True
                continue            
            # Get model info for logging
            from .ollama_client import COMPONENT_MODEL_MAP
            model_name = COMPONENT_MODEL_MAP.get(component_type, 'unknown')
            logger.info(f"[{i}/{total_components}] Generating {component_type} for '{card_name}' using {model_name}...")
            
            success = self.generate_component(uuid, component_type)
            results[component_type] = success
            
            if success:
                logger.info(f"[{i}/{total_components}] ✓ Successfully generated {component_type} for '{card_name}'")
            else:
                logger.warning(f"[{i}/{total_components}] ✗ Failed to generate {component_type} for '{card_name}'")
        
        # Final summary
        successful_count = sum(1 for success in results.values() if success)
        logger.info(f"Completed analysis for '{card_name}': {successful_count}/{total_components} components generated")
        
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
