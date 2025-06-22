from django import template
from django.utils.safestring import mark_safe
import re
import markdown
from ..scryfall_utils import ScryfallDataHelper

register = template.Library()

@register.filter
def analyze_markdown(value):
    """Convert markdown to HTML with card linking."""
    if not value:
        return ""
    
    # Configure markdown with extensions
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
    
    # Pattern to match {X} style mana symbols
    symbol_pattern = r'\{([^}]+)\}'
    
    def replace_symbol(match):
        symbol = match.group(1).upper()
        
        # Handle hybrid mana (like W/U, 2/W, etc.)
        if '/' in symbol:
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
            'W': 'w', 'U': 'u', 'B': 'b', 'R': 'r', 'G': 'g',
            'C': 'c', 'X': 'x', 'S': 's', 'T': 't', 'Q': 'q', 'E': 'e'
        }
        
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
    
    # Pattern to match {X} style mana symbols
    symbol_pattern = r'\{([^}]+)\}'
    
    def replace_symbol(match):
        symbol = match.group(1).upper()
        
        # Handle hybrid mana (like W/U, 2/W, etc.)
        if '/' in symbol:
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
            'W': 'w', 'U': 'u', 'B': 'b', 'R': 'r', 'G': 'g',
            'C': 'c', 'X': 'x', 'T': 't', 'Q': 'q', 'E': 'e', 'S': 's',
            'CHAOS': 'chaos', 'PW': 'pw'
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
def markdown_to_html(value):
    """Convert markdown to HTML."""
    if not value:
        return ""
    
    # Configure markdown with extensions
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    html_content = md.convert(value)
    
    return mark_safe(html_content)

@register.filter
def card_image(card, size='normal'):
    """Get image URL for a card."""
    return ScryfallDataHelper.get_best_image_url(card, size)

@register.filter
def card_price(card, price_type='usd'):
    """Get formatted price for a card."""
    prices = ScryfallDataHelper.get_card_prices(card)
    price_str = prices.get(price_type)
    return ScryfallDataHelper.format_price(price_str)

@register.filter
def has_enhanced_data(card):
    """Check if card has enhanced Scryfall data."""
    return ScryfallDataHelper.has_scryfall_data(card)

@register.filter
def card_legalities(card):
    """Get card format legalities."""
    return ScryfallDataHelper.get_card_legalities(card)

@register.filter
def card_scryfall_url(card):
    """Get Scryfall page URL for a card."""
    return ScryfallDataHelper.get_scryfall_url(card)

@register.filter
def card_artist(card):
    """Get card artist information."""
    return ScryfallDataHelper.get_artist_info(card)

@register.filter
def advanced_price(card, price_type='best_usd'):
    """
    Get advanced pricing with MTGjson intelligence.
    
    price_type options:
    - 'best_usd': Best USD price (TCGPlayer or average)
    - 'best_eur': Best EUR price (CardMarket)
    - 'tcgplayer': Specific TCGPlayer price
    - 'cardmarket': Specific CardMarket price
    - 'trend': Price trend percentage
    - 'category': Trend category (rising/falling/stable)
    """
    prices = card.get('prices', {})
    
    if price_type == 'best_usd':
        # Try sources in order of preference
        sources = prices.get('price_sources', {})
        for source in ['tcgplayer', 'cardkingdom']:
            if sources.get(source, 0) > 0:
                return f"${sources[source]:.2f}"
        return f"${prices.get('usd', 0):.2f}" if prices.get('usd', 0) > 0 else "N/A"
    
    elif price_type == 'best_eur':
        sources = prices.get('price_sources', {})
        if sources.get('cardmarket', 0) > 0:
            return f"€{sources['cardmarket']:.2f}"
        return f"€{prices.get('eur', 0):.2f}" if prices.get('eur', 0) > 0 else "N/A"
    
    elif price_type == 'tcgplayer':
        sources = prices.get('price_sources', {})
        tcg_price = sources.get('tcgplayer', 0)
        return f"${tcg_price:.2f}" if tcg_price > 0 else "N/A"
    
    elif price_type == 'cardmarket':
        sources = prices.get('price_sources', {})
        cm_price = sources.get('cardmarket', 0)
        return f"€{cm_price:.2f}" if cm_price > 0 else "N/A"
    
    elif price_type == 'trend':
        trend = prices.get('price_trend_30d', 0)
        if trend > 0:
            return f"+{trend:.1f}%"
        else:
            return f"{trend:.1f}%"
    
    elif price_type == 'category':
        return prices.get('trend_category', 'unknown').replace('_', ' ').title()
    
    return "N/A"

@register.filter
def price_trend_icon(card):
    """Get an icon representing the price trend."""
    prices = card.get('prices', {})
    category = prices.get('trend_category', 'unknown')
    
    icons = {
        'rising_fast': 'bi-graph-up-arrow text-success',
        'rising': 'bi-graph-up text-success',
        'stable': 'bi-dash-circle text-muted',
        'falling': 'bi-graph-down text-warning',
        'falling_fast': 'bi-graph-down-arrow text-danger',
        'unknown': 'bi-question-circle text-muted'
    }
    
    return icons.get(category, icons['unknown'])

@register.filter
def price_volatility(card):
    """Get price volatility as a user-friendly string."""
    prices = card.get('prices', {})
    volatility = prices.get('volatility', 0)
    
    if volatility > 2:
        return "High"
    elif volatility > 1:
        return "Medium"
    elif volatility > 0.5:
        return "Low"
    else:
        return "Stable"

@register.filter
def pricing_data_quality(card):
    """Get pricing data quality indicator."""
    prices = card.get('prices', {})
    sources = prices.get('data_sources', [])
    
    if len(sources) >= 3:
        return "Excellent"
    elif len(sources) >= 2:
        return "Good"
    elif len(sources) >= 1:
        return "Fair"
    else:
        return "Limited"

@register.filter
def price_comparison(card):
    """Get price comparison across sources."""
    prices = card.get('prices', {})
    sources = prices.get('price_sources', {})
    
    comparisons = []
    for source, price in sources.items():
        if price > 0:
            comparisons.append(f"{source.title()}: ${price:.2f}")
    
    return " | ".join(comparisons) if comparisons else "No price data"
