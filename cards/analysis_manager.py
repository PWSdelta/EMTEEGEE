"""
Minimal analysis manager for basic functionality.
"""

from .models import get_cards_collection


class AnalysisManager:
    """Basic analysis manager for card operations."""
    
    def get_card_by_uuid(self, card_uuid):
        """Get a card by its UUID."""
        try:
            cards_collection = get_cards_collection()
            return cards_collection.find_one({'uuid': card_uuid})
        except Exception as e:
            print(f"Error getting card {card_uuid}: {e}")
            return None
    
    def get_analysis_progress(self):
        """Get basic analysis progress stats."""
        try:
            cards_collection = get_cards_collection()
            total_cards = cards_collection.count_documents({})
            analyzed_cards = cards_collection.count_documents({'analysis.fully_analyzed': True})
            
            return {
                'total_cards': total_cards,
                'analyzed_cards': analyzed_cards,
                'pending_cards': total_cards - analyzed_cards,
                'progress_percentage': (analyzed_cards / total_cards * 100) if total_cards > 0 else 0
            }
        except Exception as e:
            print(f"Error getting analysis progress: {e}")
            return {
                'total_cards': 0,
                'analyzed_cards': 0,
                'pending_cards': 0,
                'progress_percentage': 0
            }


# Create a global instance
analysis_manager = AnalysisManager()
