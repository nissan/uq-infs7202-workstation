from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using key.
    
    Usage:
    {{ mydict|get_item:item_key }}
    """
    if dictionary is None:
        return None
        
    return dictionary.get(key)