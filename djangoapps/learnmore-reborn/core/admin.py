from django.contrib import admin
from django.utils.html import format_html
from .models import ThemeSettings, UserPreferences, AccessibilityElement

@admin.register(ThemeSettings)
class ThemeSettingsAdmin(admin.ModelAdmin):
    """Admin interface for managing theme settings."""
    list_display = ('name', 'theme_mode', 'is_default', 'color_preview', 'updated_at')
    list_filter = ('theme_mode', 'is_default')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'color_palette_preview')
    save_on_top = True
    
    fieldsets = (
        ('Theme Information', {
            'fields': ('name', 'is_default', 'theme_mode')
        }),
        ('Color Scheme', {
            'fields': ('color_palette_preview', 'primary_color', 'secondary_color', 'success_color', 
                      'danger_color', 'warning_color', 'info_color', 'background_color', 'text_color')
        }),
        ('Typography', {
            'fields': ('font_family', 'base_font_size', 'heading_font_family')
        }),
        ('Layout', {
            'fields': ('border_radius', 'spacing_unit', 'container_max_width')
        }),
        ('Accessibility', {
            'fields': ('enable_animations', 'reduce_motion', 'high_contrast_mode', 
                      'font_scaling', 'increase_target_size')
        }),
        ('Custom CSS', {
            'fields': ('custom_css',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_preview(self, obj):
        """Show a small preview of the primary color."""
        return format_html(
            '<div style="background-color: {}; width: 30px; height: 30px; border-radius: 5px;"></div>',
            obj.primary_color
        )
    color_preview.short_description = 'Primary Color'
    
    def color_palette_preview(self, obj):
        """Show a preview of the entire color palette."""
        colors = {
            'Primary': obj.primary_color,
            'Secondary': obj.secondary_color,
            'Success': obj.success_color,
            'Danger': obj.danger_color,
            'Warning': obj.warning_color,
            'Info': obj.info_color,
            'Background': obj.background_color,
            'Text': obj.text_color,
        }
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for name, color in colors.items():
            html += f'''
                <div style="text-align: center;">
                    <div style="background-color: {color}; width: 50px; height: 50px; 
                         border-radius: 5px; margin-bottom: 5px;"></div>
                    <div>{name}</div>
                    <div>{color}</div>
                </div>
            '''
        html += '</div>'
        
        return format_html(html)
    color_palette_preview.short_description = 'Color Palette Preview'


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for managing user preferences."""
    list_display = ('user', 'theme_mode', 'text_size', 'motion_preference', 'high_contrast', 'updated_at')
    list_filter = ('theme_mode', 'text_size', 'motion_preference', 'high_contrast')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Theme Preferences', {
            'fields': ('theme_mode', 'use_custom_colors', 'primary_color')
        }),
        ('Accessibility Preferences', {
            'fields': ('text_size', 'motion_preference', 'high_contrast', 'increase_text_spacing',
                      'dyslexia_friendly_font', 'screen_reader_optimization', 
                      'keyboard_navigation_optimization')
        }),
        ('Navigation Preferences', {
            'fields': ('simplified_navigation', 'show_content_outlines')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AccessibilityElement)
class AccessibilityElementAdmin(admin.ModelAdmin):
    """Admin interface for managing accessibility elements."""
    list_display = ('selector', 'element_type', 'aria_role', 'is_skip_target', 'last_validated')
    list_filter = ('element_type', 'is_skip_target')
    search_fields = ('selector', 'aria_label', 'aria_description', 'notes')
    
    fieldsets = (
        ('Element Information', {
            'fields': ('selector', 'element_type')
        }),
        ('ARIA Properties', {
            'fields': ('aria_label', 'aria_role', 'aria_description')
        }),
        ('Skip Navigation', {
            'fields': ('is_skip_target', 'skip_target_name')
        }),
        ('Keyboard Navigation', {
            'fields': ('tab_index', 'keyboard_shortcut')
        }),
        ('Additional Information', {
            'fields': ('additional_attributes', 'notes', 'last_validated')
        }),
    )