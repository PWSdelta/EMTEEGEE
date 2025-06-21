"""
Scryfall data utilities for enhanced card information.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class ScryfallDataHelper:
    """Helper class for working with Scryfall data in cards."""
    
    @staticmethod
    def get_card_images(card: Dict[str, Any]) -> Dict[str, str]:
        """Extract image URLs from card data."""
        # Direct imageUris field (new structure)
        return card.get('imageUris', {})
    
    @staticmethod
    def get_card_prices(card: Dict[str, Any]) -> Dict[str, str]:
        """Extract pricing information from card data."""
        return card.get('prices', {})
    
    @staticmethod
    def get_purchase_links(card: Dict[str, Any]) -> Dict[str, str]:
        """Extract purchase URLs from card data."""
        return card.get('purchaseUris', {})
    
    @staticmethod
    def get_card_legalities(card: Dict[str, Any]) -> Dict[str, str]:
        """Extract format legalities from card data."""
        return card.get('legalities', {})
    
    @staticmethod
    def get_set_info(card: Dict[str, Any]) -> Dict[str, str]:
        """Extract set information from card data."""
        return {
            'code': card.get('setCode', ''),
            'name': card.get('setName', ''),
            'released_at': card.get('releasedAt', ''),
        }
    
    @staticmethod
    def get_best_image_url(card: Dict[str, Any], size: str = 'normal') -> Optional[str]:
        """Get the best available image URL for a card."""
        images = ScryfallDataHelper.get_card_images(card)
        
        # Preferred order of image sizes
        size_preferences = {
            'small': ['small', 'normal', 'large'],
            'normal': ['normal', 'large', 'small'],
            'large': ['large', 'normal', 'small'],
            'png': ['png', 'border_crop', 'large', 'normal'],
            'art_crop': ['art_crop', 'large', 'normal'],
            'border_crop': ['border_crop', 'large', 'normal']
        }
        
        preferences = size_preferences.get(size, ['normal', 'large', 'small'])
        
        for preferred_size in preferences:
            if preferred_size in images:
                return images[preferred_size]
        
        # Fallback to any available image
        if images:
            return next(iter(images.values()))
        
        return None
    
    @staticmethod
    def format_price(price_str: Optional[str]) -> str:
        """Format a price string for display."""
        if not price_str:
            return "N/A"
        
        try:
            price = float(price_str)
            return f"${price:.2f}"
        except (ValueError, TypeError):
            return "N/A"
      @staticmethod
    def get_color_identity_symbols(card: Dict[str, Any]) -> List[str]:
        """Get color identity as mana symbols."""
        color_identity = card.get('colorIdentity', [])
        
        # Convert color letters to symbol names
        color_map = {
            'W': 'w', 'U': 'u', 'B': 'b', 'R': 'r', 'G': 'g', 'C': 'c'
        }
        
        return [color_map.get(color, color.lower()) for color in color_identity]
    
    @staticmethod
    def is_card_legal_in_format(card: Dict[str, Any], format_name: str) -> bool:
        """Check if a card is legal in a specific format."""
        legalities = ScryfallDataHelper.get_card_legalities(card)
        return legalities.get(format_name.lower(), 'not_legal') == 'legal'
    
    @staticmethod
    def get_card_keywords(card: Dict[str, Any]) -> List[str]:
        """Extract keywords from card data."""
        return card.get('keywords', [])
    
    @staticmethod
    def get_artist_info(card: Dict[str, Any]) -> str:
        """Get artist information."""
        return card.get('artist', 'Unknown')
    
    @staticmethod
    def has_scryfall_data(card: Dict[str, Any]) -> bool:
        """Check if card has Scryfall enhancement data."""
        return bool(card.get('scryfallId') or card.get('imageUris') or card.get('prices'))
    
    @staticmethod
    def get_scryfall_url(card: Dict[str, Any]) -> Optional[str]:
        """Get the Scryfall page URL for this card."""
        return card.get('scryfallUri')

# Make helper functions available as template filters
def register_scryfall_template_filters():
    """Register Scryfall helper functions as Django template filters."""
    from django import template
    from django.utils.safestring import mark_safe
    
    register = template.Library()
    
    @register.filter
    def scryfall_image(card, size='normal'):
        """Get Scryfall image URL for a card."""
        return ScryfallDataHelper.get_best_image_url(card, size)
    
    @register.filter
    def scryfall_price(card, price_type='usd'):
        """Get formatted price for a card."""
        prices = ScryfallDataHelper.get_card_prices(card)
        price_str = prices.get(price_type)
        return ScryfallDataHelper.format_price(price_str)
    
    @register.filter
    def has_scryfall(card):
        """Check if card has Scryfall data."""
        return ScryfallDataHelper.has_scryfall_data(card)
    
    @register.filter
    def scryfall_legalities(card):
        """Get card format legalities."""
        return ScryfallDataHelper.get_card_legalities(card)
    
    return register
