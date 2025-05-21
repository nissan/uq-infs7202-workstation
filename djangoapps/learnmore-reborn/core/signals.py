from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import ThemeSettings, UserPreferences, AccessibilityElement

@receiver(post_save, sender=ThemeSettings)
def theme_settings_changed(sender, instance, **kwargs):
    """Clear cached theme data when theme settings change."""
    cache.delete('default_theme')
    cache.delete(f'theme_{instance.id}')

@receiver(post_delete, sender=ThemeSettings)
def theme_settings_deleted(sender, instance, **kwargs):
    """Clear cached theme data when a theme is deleted."""
    cache.delete('default_theme')
    cache.delete(f'theme_{instance.id}')

@receiver(post_save, sender=UserPreferences)
def user_preferences_changed(sender, instance, **kwargs):
    """Clear cached user preferences when they change."""
    cache.delete(f'user_preferences_{instance.user.id}')

@receiver(post_save, sender=AccessibilityElement)
def accessibility_element_changed(sender, instance, **kwargs):
    """Clear cached accessibility elements when they change."""
    cache.delete('accessibility_elements')