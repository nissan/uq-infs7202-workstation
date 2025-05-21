from rest_framework import serializers
from .models import ThemeSettings, UserPreferences, AccessibilityElement

class ThemeSettingsSerializer(serializers.ModelSerializer):
    """Serializer for theme settings."""
    
    class Meta:
        model = ThemeSettings
        fields = [
            'id', 'name', 'is_default', 'theme_mode',
            'primary_color', 'secondary_color', 'success_color', 
            'danger_color', 'warning_color', 'info_color', 
            'background_color', 'text_color',
            'font_family', 'base_font_size', 'heading_font_family',
            'border_radius', 'spacing_unit', 'container_max_width',
            'enable_animations', 'reduce_motion', 'high_contrast_mode', 
            'font_scaling', 'increase_target_size',
            'custom_css', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPreferences
        fields = [
            'id', 'user', 'username', 'theme_mode', 'motion_preference', 'text_size',
            'use_custom_colors', 'primary_color', 'high_contrast', 
            'increase_text_spacing', 'dyslexia_friendly_font',
            'screen_reader_optimization', 'keyboard_navigation_optimization',
            'simplified_navigation', 'show_content_outlines',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'username']
    
    def get_username(self, obj):
        """Get the user's username."""
        return obj.user.username


class AccessibilityElementSerializer(serializers.ModelSerializer):
    """Serializer for accessibility elements."""
    
    class Meta:
        model = AccessibilityElement
        fields = [
            'id', 'selector', 'element_type', 'aria_label', 'aria_role',
            'aria_description', 'additional_attributes', 'is_skip_target',
            'skip_target_name', 'tab_index', 'keyboard_shortcut',
            'notes', 'last_validated'
        ]


class AltTextSerializer(serializers.Serializer):
    """Serializer for alt text management."""
    element_id = serializers.CharField()
    element_type = serializers.CharField()
    alt_text = serializers.CharField()
    context = serializers.CharField(required=False, allow_blank=True)
    
    def validate_element_type(self, value):
        """Validate the element type."""
        valid_types = ['image', 'button', 'icon', 'chart', 'map', 'video', 'audio', 'custom']
        if value not in valid_types:
            raise serializers.ValidationError(f"Element type must be one of: {', '.join(valid_types)}")
        return value


class NavigationPreferencesSerializer(serializers.Serializer):
    """Serializer for navigation preferences."""
    simplified_navigation = serializers.BooleanField(default=False)
    show_content_outlines = serializers.BooleanField(default=False)
    show_skip_links = serializers.BooleanField(default=True)
    use_keyboard_shortcuts = serializers.BooleanField(default=True)
    show_breadcrumbs = serializers.BooleanField(default=True)
    navigation_position = serializers.ChoiceField(
        choices=['top', 'left', 'right', 'bottom'],
        default='top'
    )


class ThemePreferencesSerializer(serializers.Serializer):
    """Serializer for theme preferences updates."""
    theme_mode = serializers.ChoiceField(
        choices=['system', 'light', 'dark', 'high_contrast'],
        default='system'
    )
    motion_preference = serializers.ChoiceField(
        choices=['system', 'full', 'reduced', 'none'],
        default='system'
    )
    text_size = serializers.ChoiceField(
        choices=['system', 'small', 'medium', 'large', 'x-large'],
        default='system'
    )
    use_custom_colors = serializers.BooleanField(default=False)
    primary_color = serializers.CharField(max_length=20, required=False, allow_blank=True)
    high_contrast = serializers.BooleanField(default=False)