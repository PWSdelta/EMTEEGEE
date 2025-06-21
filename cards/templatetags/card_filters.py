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
