from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def icon(name, class_name=''):
    """
    Render a Lucide icon with optional additional classes.
    Usage: {% icon 'BookOpen' class='w-6 h-6' %}
    """
    context = {
        'icon': name,
        'class': class_name
    }
    return render_to_string('components/atoms/icons/lucide.html', context) 