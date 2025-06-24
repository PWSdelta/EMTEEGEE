"""
Template filters for the cards app.
"""

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary."""
    return dictionary.get(key)

@register.filter
def replace(value, arg):
    """Replace characters in a string."""
    if len(arg.split(',')) == 2:
        old, new = arg.split(',')
        return value.replace(old, new)
    return value

@register.filter
def split(value, arg):
    """Split a string by delimiter."""
    return value.split(arg)
