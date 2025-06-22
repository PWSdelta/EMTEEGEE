"""
Custom template filters for the cards app.
"""

import re
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def markdown_to_html(value):
    """
    Convert markdown text to HTML with card name linking.
    
    This filter:
    1. Converts markdown to HTML
    2. Converts [[card name]] patterns to clickable links
    """
    if not value:
        return ""
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    html_content = md.convert(value)
    
    # Convert [[card name]] to links
    # Pattern matches [[anything]] and creates a search link
    card_link_pattern = r'\[\[([^\]]+)\]\]'
    
    def replace_card_link(match):
        card_name = match.group(1).strip()
        # Create a link to search for this card
        return f'<a href="/browse/?q={card_name}" class="card-link" title="Search for {card_name}"><strong>{card_name}</strong></a>'
    
    # Replace all [[card name]] patterns with links
    html_content = re.sub(card_link_pattern, replace_card_link, html_content)
    
    return mark_safe(html_content)

@register.filter
def component_icon(component_type):
    """Return an emoji icon for each component type."""
    icons = {
        'tactical_analysis': '🎯',
        'thematic_analysis': '🎨', 
        'play_tips': '💡',
        'combo_suggestions': '⚡',
        'power_level_assessment': '⚖️',
        'format_analysis': '🏆',
        'synergy_analysis': '🔗',
        'competitive_analysis': '🥇',
        'budget_alternatives': '💰',
        'historical_context': '📚',
        'art_flavor_analysis': '🖼️',
        'investment_outlook': '📈',
        'deck_archetypes': '🏗️',
        'meta_positioning': '🌐',
        'new_player_guide': '🆕',
        'advanced_interactions': '🧠',
        'mulligan_considerations': '🔄',
        'sideboard_guide': '📋',
        'rules_clarifications': '📖',
        'design_philosophy': '💭'
    }
    return icons.get(component_type, '📄')

@register.filter  
def component_title(component_type):
    """Return a human-readable title for each component type."""
    titles = {
        'tactical_analysis': 'Tactical Analysis',
        'thematic_analysis': 'Thematic Analysis',
        'play_tips': 'Play Tips', 
        'combo_suggestions': 'Combo Suggestions',
        'power_level_assessment': 'Power Level Assessment',
        'format_analysis': 'Format Analysis',
        'synergy_analysis': 'Synergy Analysis',
        'competitive_analysis': 'Competitive Analysis',
        'budget_alternatives': 'Budget Alternatives',
        'historical_context': 'Historical Context',
        'art_flavor_analysis': 'Art & Flavor Analysis',
        'investment_outlook': 'Investment Outlook',
        'deck_archetypes': 'Deck Archetypes',
        'meta_positioning': 'Meta Positioning',
        'new_player_guide': 'New Player Guide',
        'advanced_interactions': 'Advanced Interactions',
        'mulligan_considerations': 'Mulligan Considerations',
        'sideboard_guide': 'Sideboard Guide',
        'rules_clarifications': 'Rules Clarifications',
        'design_philosophy': 'Design Philosophy'
    }
    return titles.get(component_type, component_type.replace('_', ' ').title())

@register.filter
def scryfall_mana_symbols(mana_cost):
    """Convert mana cost string to Scryfall symbol images."""
    if not mana_cost:
        return ""
    
    # Convert to string and check if already processed
    cost_str = str(mana_cost)
    if '<img' in cost_str and 'mana-symbol' in cost_str:
        return mark_safe(cost_str)
    
    import re
    
    # Pattern to match {X} style mana symbols
    symbol_pattern = r'\{([^}]+)\}'
    
    def replace_symbol(match):
        symbol = match.group(1).upper()
          # Handle hybrid mana (like W/U, 2/W, etc.)
        if '/' in symbol:
            # For hybrid symbols, create proper name
            parts = symbol.split('/')
            if len(parts) == 2:
                hybrid_name = ''.join(part.lower() for part in parts)
                return f'<img src="https://svgs.scryfall.io/card-symbols/{hybrid_name}.svg" alt="{{{symbol}}}" class="mana-symbol" title="Mana cost: {{{symbol}}}">'
        
        # Handle numeric symbols (0-20)
        if symbol.isdigit():
            num = int(symbol)
            if 0 <= num <= 20:
                return f'<img src="https://svgs.scryfall.io/card-symbols/{num}.svg" alt="{{{symbol}}}" class="mana-symbol" title="Mana cost: {{{symbol}}}">'
        
        # Handle basic mana symbols
        symbol_map = {
            'W': 'w', 'U': 'u', 'B': 'b', 'R': 'r', 'G': 'g',  # Basic colors
            'C': 'c',  # Colorless
            'X': 'x',  # Variable
            'S': 's',  # Snow
            'T': 't',  # Tap
            'Q': 'q',  # Untap
            'E': 'e',  # Energy
        }
        
        # Get the symbol or use lowercase version
        scryfall_symbol = symbol_map.get(symbol, symbol.lower())
        
        return f'<img src="https://svgs.scryfall.io/card-symbols/{scryfall_symbol}.svg" alt="{{{symbol}}}" class="mana-symbol" title="Mana cost: {{{symbol}}}">'
    
    # Replace all {X} patterns with symbol images
    html_with_symbols = re.sub(symbol_pattern, replace_symbol, cost_str)
    
    return mark_safe(html_with_symbols)


@register.filter
def scryfall_parse_text(card_text):
    """Parse card text and replace mana symbols with Scryfall images."""
    if not card_text:
        return ""
    
    # Convert to string and check if already processed
    text_str = str(card_text)
    if '<img' in text_str and 'mana-symbol' in text_str:
        return mark_safe(text_str)
    
    import re
    
    # Pattern to match {X} style mana symbols in card text
    symbol_pattern = r'\{([^}]+)\}'
    
    def replace_symbol(match):
        symbol = match.group(1).upper()
        
        # Handle hybrid mana (e.g., {W/U})
        if '/' in symbol:
            # For hybrid symbols, use the format like "wu" for {W/U}
            parts = symbol.split('/')
            if len(parts) == 2:
                hybrid_name = ''.join(part.lower() for part in parts)
                return f'<img src="https://svgs.scryfall.io/card-symbols/{hybrid_name}.svg" alt="{{{symbol}}}" class="mana-symbol-text" title="{{{symbol}}}">'
            
        # Handle numeric symbols (0-20)
        if symbol.isdigit():
            num = int(symbol)
            if 0 <= num <= 20:
                return f'<img src="https://svgs.scryfall.io/card-symbols/{num}.svg" alt="{{{symbol}}}" class="mana-symbol-text" title="{{{symbol}}}">'
        
        # Handle common symbols in card text
        symbol_map = {
            'W': 'w', 'U': 'u', 'B': 'b', 'R': 'r', 'G': 'g',  # Basic colors
            'C': 'c',  # Colorless
            'X': 'x',  # Variable
            'T': 't',  # Tap
            'Q': 'q',  # Untap
            'E': 'e',  # Energy
            'S': 's',  # Snow
            'CHAOS': 'chaos',
            'PW': 'pw'
        }
        
        # Get the appropriate symbol name
        scryfall_symbol = symbol_map.get(symbol, symbol.lower())
        
        return f'<img src="https://svgs.scryfall.io/card-symbols/{scryfall_symbol}.svg" alt="{{{symbol}}}" class="mana-symbol-text" title="{{{symbol}}}">'
    
    # Replace all {X} patterns with symbol images
    html_with_symbols = re.sub(symbol_pattern, replace_symbol, text_str)
    
    return mark_safe(html_with_symbols)


@register.filter  
def format_card_types(type_line):
    """Format card type line with better spacing and emphasis."""
    if not type_line:
        return ""
        
    # Split on em-dash if present (separates types from subtypes)
    if '—' in type_line:
        main_types, subtypes = type_line.split('—', 1)
        return mark_safe(f'<strong>{main_types.strip()}</strong> — <em>{subtypes.strip()}</em>')
    else:
        return mark_safe(f'<strong>{type_line}</strong>')

@register.filter
def scryfall_parse_text_with_breaks(card_text):
    """Parse card text, replace mana symbols, and handle line breaks properly."""
    if not card_text:
        return ""
    
    # First, parse mana symbols
    parsed_text = scryfall_parse_text(card_text)
    
    # Then handle line breaks manually to avoid interference with HTML
    lines = str(parsed_text).split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            html_lines.append(f'<p>{line}</p>')
        else:
            html_lines.append('<br>')
    
    return mark_safe(''.join(html_lines))

@register.filter
def card_image(card, image_type='normal'):
    """
    Get card image URL for a specific image type.
    
    Args:
        card: Card object/dict from MongoDB
        image_type: Type of image ('normal', 'art_crop', 'small', 'large', etc.)
    
    Returns:
        Image URL string or None if not available
    """
    if not card:
        return None
        
    # Get imageUris from the card
    image_uris = card.get('imageUris', {})
    
    if not image_uris:
        return None
    
    # Try to get the requested image type
    if image_type in image_uris:
        return image_uris[image_type]
    
    # Fallback hierarchy
    fallback_order = ['normal', 'large', 'small', 'art_crop']
    
    for fallback_type in fallback_order:
        if fallback_type in image_uris:
            return image_uris[fallback_type]
    
    return None

@register.filter
def format_card_text(card_text):
    """Format card text with mana symbols and proper line breaks."""
    if not card_text:
        return ""
    
    # Use the existing scryfall_parse_text_with_breaks filter
    return scryfall_parse_text_with_breaks(card_text)

@register.filter
def analyze_markdown(content, card=None):
    """Process markdown content with card linking for analysis components."""
    if not content:
        return ""
    
    # Use the existing markdown_to_html filter which handles card linking
    return markdown_to_html(content)
