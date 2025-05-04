from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('components/elements/button.html')
def button(text, url="#", variant="primary", size="md", classes=""):
    """
    Renders a button component.
    
    Usage:
    {% load component_tags %}
    {% button "Get Started" url=signup_url variant="primary" size="lg" %}
    """
    return {
        'text': text,
        'url': url,
        'variant': variant,
        'size': size,
        'classes': classes
    }

@register.inclusion_tag('components/elements/card.html')
def card(title, content, button_text=None, button_url=None, image_url=None, classes=""):
    """
    Renders a card component.
    
    Usage:
    {% load component_tags %}
    {% card "Card Title" "Card content text" button_text="Learn More" button_url=learn_more_url %}
    """
    return {
        'title': title,
        'content': content,
        'button_text': button_text,
        'button_url': button_url,
        'image_url': image_url,
        'classes': classes
    }

@register.inclusion_tag('components/sections/hero.html')
def hero_section(title, subtitle, image_url, primary_button_text=None, primary_button_url=None, 
                secondary_button_text=None, secondary_button_url=None, classes=""):
    """
    Renders a hero section.
    
    Usage:
    {% load component_tags %}
    {% hero_section "Main Title" "Subtitle text" image_url=image_path 
       primary_button_text="Get Started" primary_button_url=url %}
    """
    return {
        'title': mark_safe(title),  # Allow HTML in title
        'subtitle': subtitle,
        'image_url': image_url,
        'primary_button_text': primary_button_text,
        'primary_button_url': primary_button_url,
        'secondary_button_text': secondary_button_text,
        'secondary_button_url': secondary_button_url,
        'classes': classes
    }

@register.inclusion_tag('components/sections/feature.html')
def feature_section(title="Powerful Features", subtitle=None, feature_items=None):
    """
    Renders a features section.
    
    Usage:
    {% load component_tags %}
    {% feature_section "Our Features" "Subtitle text" feature_items=features %}
    
    Where features is a list of dictionaries with title, description, and icon keys.
    """
    if subtitle is None:
        subtitle = "Our platform combines cutting-edge technology with intuitive design."
        
    return {
        'title': title,
        'subtitle': subtitle,
        'features': feature_items  # Note: renamed to match the template's variable name
    }

@register.inclusion_tag('components/sections/cta.html')
def cta_section(title=None, subtitle=None, button_text=None, button_url=None, classes=""):
    """
    Renders a call-to-action section.
    
    Usage:
    {% load component_tags %}
    {% cta_section "Ready to get started?" "Join today" button_text="Sign Up" button_url=signup_url %}
    """
    return {
        'title': title,
        'subtitle': subtitle,
        'button_text': button_text,
        'button_url': button_url,
        'classes': classes
    }

@register.inclusion_tag('components/minimal-button.html')
def minimal_button(text, url="#"):
    """
    A simpler button with fewer parameters for testing.
    
    Usage:
    {% load component_tags %}
    {% minimal_button "Text" "url" %}
    """
    return {
        'text': text,
        'url': url
    }

@register.simple_tag
def icon(name, size="md", classes=""):
    """
    Renders a Lucide icon.
    
    Usage:
    {% load component_tags %}
    {% icon "user" size="lg" classes="text-primary-500" %}
    """
    sizes = {
        "sm": "w-4 h-4",
        "md": "w-6 h-6",
        "lg": "w-8 h-8",
    }
    
    size_class = sizes.get(size, sizes["md"])
    
    return mark_safe(f'<i data-lucide="{name}" class="{size_class} {classes}"></i>')