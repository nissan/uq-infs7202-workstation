from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ThemeSettings(models.Model):
    """
    Global theme settings for the platform.
    
    This model stores the default theme settings that apply across the platform,
    including color schemes, typography, and accessibility defaults.
    """
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('high_contrast', 'High Contrast'),
        ('custom', 'Custom'),
    ]
    
    FONT_FAMILY_CHOICES = [
        ('system', 'System Default'),
        ('inter', 'Inter'),
        ('roboto', 'Roboto'),
        ('open_sans', 'Open Sans'),
        ('montserrat', 'Montserrat'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    theme_mode = models.CharField(max_length=20, choices=THEME_CHOICES, default='light')
    
    # Color scheme
    primary_color = models.CharField(max_length=20, default='#007bff')
    secondary_color = models.CharField(max_length=20, default='#6c757d')
    success_color = models.CharField(max_length=20, default='#28a745')
    danger_color = models.CharField(max_length=20, default='#dc3545')
    warning_color = models.CharField(max_length=20, default='#ffc107')
    info_color = models.CharField(max_length=20, default='#17a2b8')
    background_color = models.CharField(max_length=20, default='#ffffff')
    text_color = models.CharField(max_length=20, default='#212529')
    
    # Typography settings
    font_family = models.CharField(max_length=20, choices=FONT_FAMILY_CHOICES, default='system')
    base_font_size = models.CharField(max_length=10, default='16px')
    heading_font_family = models.CharField(max_length=20, choices=FONT_FAMILY_CHOICES, default='system')
    
    # Layout settings
    border_radius = models.CharField(max_length=10, default='0.25rem')
    spacing_unit = models.CharField(max_length=10, default='1rem')
    container_max_width = models.CharField(max_length=10, default='1140px')
    
    # Accessibility settings
    enable_animations = models.BooleanField(default=True)
    reduce_motion = models.BooleanField(default=False)
    high_contrast_mode = models.BooleanField(default=False)
    font_scaling = models.FloatField(default=1.0)
    increase_target_size = models.BooleanField(default=False)
    
    # Custom CSS
    custom_css = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Theme Setting'
        verbose_name_plural = 'Theme Settings'
    
    def __str__(self):
        return f"{self.name} Theme"
    
    def save(self, *args, **kwargs):
        """Ensure only one default theme exists"""
        if self.is_default:
            # Set all other themes as non-default
            ThemeSettings.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UserPreferences(models.Model):
    """
    User-specific preferences for theme and accessibility.
    
    This model allows users to customize their own experience, overriding
    the default platform settings for personalization.
    """
    THEME_PREFERENCES = [
        ('system', 'Use System Preference'),
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('high_contrast', 'High Contrast'),
    ]
    
    MOTION_PREFERENCES = [
        ('system', 'Use System Preference'),
        ('full', 'Full Animations'),
        ('reduced', 'Reduced Animations'),
        ('none', 'No Animations'),
    ]
    
    TEXT_SIZE_PREFERENCES = [
        ('system', 'Use System Preference'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('x-large', 'Extra Large'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='theme_preferences')
    theme_mode = models.CharField(max_length=20, choices=THEME_PREFERENCES, default='system')
    motion_preference = models.CharField(max_length=20, choices=MOTION_PREFERENCES, default='system')
    text_size = models.CharField(max_length=20, choices=TEXT_SIZE_PREFERENCES, default='system')
    
    # Custom colors (if desired)
    use_custom_colors = models.BooleanField(default=False)
    primary_color = models.CharField(max_length=20, blank=True)
    
    # Accessibility preferences
    high_contrast = models.BooleanField(default=False)
    increase_text_spacing = models.BooleanField(default=False)
    dyslexia_friendly_font = models.BooleanField(default=False)
    screen_reader_optimization = models.BooleanField(default=False)
    keyboard_navigation_optimization = models.BooleanField(default=False)
    
    # Navigation preferences
    simplified_navigation = models.BooleanField(default=False)
    show_content_outlines = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


class AccessibilityElement(models.Model):
    """
    Model to store custom accessibility information for site elements.
    
    This model allows ARIA labels, roles, and other accessibility information
    to be added to specific elements without modifying their base templates.
    """
    ELEMENT_TYPES = [
        ('global', 'Global Element'),
        ('navigation', 'Navigation Element'),
        ('course', 'Course Element'),
        ('quiz', 'Quiz Element'),
        ('content', 'Content Element'),
        ('form', 'Form Element'),
        ('custom', 'Custom Element'),
    ]
    
    selector = models.CharField(max_length=255, help_text='CSS selector for the element')
    element_type = models.CharField(max_length=20, choices=ELEMENT_TYPES, default='custom')
    aria_label = models.CharField(max_length=255, blank=True)
    aria_role = models.CharField(max_length=50, blank=True)
    aria_description = models.TextField(blank=True)
    
    # Additional attributes (as JSON)
    additional_attributes = models.JSONField(default=dict, blank=True)
    
    # Skip link target
    is_skip_target = models.BooleanField(default=False)
    skip_target_name = models.CharField(max_length=50, blank=True)
    
    # Keyboard navigation
    tab_index = models.IntegerField(null=True, blank=True)
    keyboard_shortcut = models.CharField(max_length=20, blank=True)
    
    # Documentation/notes
    notes = models.TextField(blank=True, help_text='Notes for developers and content editors')
    
    # Validation timestamp
    last_validated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Accessibility Element'
        verbose_name_plural = 'Accessibility Elements'
        unique_together = ('selector', 'element_type')
    
    def __str__(self):
        return f"{self.element_type}: {self.selector}"