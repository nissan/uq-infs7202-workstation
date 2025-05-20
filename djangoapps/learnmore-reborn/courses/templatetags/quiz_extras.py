from django import template
import re

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

@register.filter
def youtube_embed_url(url):
    """Convert a YouTube URL to an embed URL.
    
    Supports both youtube.com/watch?v=VIDEO_ID and youtu.be/VIDEO_ID formats.
    
    Usage: {{ youtube_url|youtube_embed_url }}
    """
    if not url:
        return ''
        
    # Regular YouTube URLs (youtube.com/watch?v=VIDEO_ID)
    watch_pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)'
    watch_match = re.match(watch_pattern, url)
    
    if watch_match:
        video_id = watch_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # Short YouTube URLs (youtu.be/VIDEO_ID)
    short_pattern = r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)'
    short_match = re.match(short_pattern, url)
    
    if short_match:
        video_id = short_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # If no matches found, return the original URL
    return url