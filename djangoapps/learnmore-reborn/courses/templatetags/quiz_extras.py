from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary safely.
    
    Usage: {{ user_quiz_attempts|get_item:quiz.id }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

@register.filter
def mod(value, arg):
    """Return the modulo of value and argument."""
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

@register.filter
def mapattr(sequence, attr):
    """Map an attribute across a sequence of objects."""
    return [getattr(item, attr) for item in sequence]

@register.filter
def sum_list(sequence):
    """Sum a list of values."""
    try:
        return sum(sequence)
    except (ValueError, TypeError):
        return None