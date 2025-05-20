from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary safely."""
    return dictionary.get(key)

@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def div(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

@register.filter
def mod(value, arg):
    """Returns the remainder of dividing the value by the argument."""
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

@register.filter
def mapattr(objects, attr):
    """Maps an attribute or method across all objects in a sequence."""
    if not objects:
        return []
        
    results = []
    for obj in objects:
        if hasattr(obj, attr):
            attr_value = getattr(obj, attr)
            if callable(attr_value):
                results.append(attr_value())
            else:
                results.append(attr_value)
    return results

@register.filter
def sum(values):
    """Sums a list of values."""
    try:
        return sum(float(v or 0) for v in values)
    except (ValueError, TypeError):
        return None