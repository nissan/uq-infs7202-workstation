from django import template

register = template.Library()

@register.simple_tag
def hello(name="World"):
    """
    A very simple tag to check if template tags are working.
    
    Usage:
    {% load simple_tags %}
    {% hello "Name" %}
    """
    return f"Hello, {name}!"