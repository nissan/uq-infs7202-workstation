from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_POST

from .models import ThemeSettings, UserPreferences, AccessibilityElement

def theme_settings(request):
    """
    View for users to manage their theme settings.
    """
    # Get the user's preferences, create if it doesn't exist
    if request.user.is_authenticated:
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    else:
        preferences = None
    
    # Get all available themes
    themes = ThemeSettings.objects.all()
    
    # Get the default theme
    default_theme = ThemeSettings.objects.filter(is_default=True).first()
    if not default_theme and themes.exists():
        default_theme = themes.first()
    
    context = {
        'preferences': preferences,
        'themes': themes,
        'default_theme': default_theme,
    }
    
    return render(request, 'core/theme_settings.html', context)

@login_required
def user_preferences(request):
    """
    View for users to manage their preferences.
    """
    # Get the user's preferences, create if it doesn't exist
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences based on form data
        preferences.theme_mode = request.POST.get('theme_mode', preferences.theme_mode)
        preferences.motion_preference = request.POST.get('motion_preference', preferences.motion_preference)
        preferences.text_size = request.POST.get('text_size', preferences.text_size)
        
        # Boolean fields
        preferences.high_contrast = 'high_contrast' in request.POST
        preferences.increase_text_spacing = 'increase_text_spacing' in request.POST
        preferences.dyslexia_friendly_font = 'dyslexia_friendly_font' in request.POST
        preferences.screen_reader_optimization = 'screen_reader_optimization' in request.POST
        preferences.keyboard_navigation_optimization = 'keyboard_navigation_optimization' in request.POST
        preferences.simplified_navigation = 'simplified_navigation' in request.POST
        preferences.show_content_outlines = 'show_content_outlines' in request.POST
        
        # Custom colors
        preferences.use_custom_colors = 'use_custom_colors' in request.POST
        if preferences.use_custom_colors:
            preferences.primary_color = request.POST.get('primary_color', '')
        
        preferences.save()
        messages.success(request, 'Your preferences have been updated.')
        return redirect('user-preferences')
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'core/user_preferences.html', context)

@login_required
def theme_editor(request):
    """
    View for admins to edit theme settings.
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('theme-settings')
    
    # Get the theme ID from the query parameters, or use the default theme
    theme_id = request.GET.get('theme_id')
    if theme_id:
        theme = get_object_or_404(ThemeSettings, id=theme_id)
    else:
        theme = ThemeSettings.objects.filter(is_default=True).first()
        if not theme:
            theme = ThemeSettings.objects.first()
    
    if request.method == 'POST':
        # Update the theme based on form data
        
        # Basic information
        theme.name = request.POST.get('name', theme.name)
        theme.theme_mode = request.POST.get('theme_mode', theme.theme_mode)
        theme.is_default = 'is_default' in request.POST
        
        # Color scheme
        theme.primary_color = request.POST.get('primary_color', theme.primary_color)
        theme.secondary_color = request.POST.get('secondary_color', theme.secondary_color)
        theme.success_color = request.POST.get('success_color', theme.success_color)
        theme.danger_color = request.POST.get('danger_color', theme.danger_color)
        theme.warning_color = request.POST.get('warning_color', theme.warning_color)
        theme.info_color = request.POST.get('info_color', theme.info_color)
        theme.background_color = request.POST.get('background_color', theme.background_color)
        theme.text_color = request.POST.get('text_color', theme.text_color)
        
        # Typography
        theme.font_family = request.POST.get('font_family', theme.font_family)
        theme.base_font_size = request.POST.get('base_font_size', theme.base_font_size)
        theme.heading_font_family = request.POST.get('heading_font_family', theme.heading_font_family)
        
        # Layout
        theme.border_radius = request.POST.get('border_radius', theme.border_radius)
        theme.spacing_unit = request.POST.get('spacing_unit', theme.spacing_unit)
        theme.container_max_width = request.POST.get('container_max_width', theme.container_max_width)
        
        # Accessibility
        theme.enable_animations = 'enable_animations' in request.POST
        theme.reduce_motion = 'reduce_motion' in request.POST
        theme.high_contrast_mode = 'high_contrast_mode' in request.POST
        theme.font_scaling = float(request.POST.get('font_scaling', theme.font_scaling))
        theme.increase_target_size = 'increase_target_size' in request.POST
        
        # Custom CSS
        theme.custom_css = request.POST.get('custom_css', theme.custom_css)
        
        theme.save()
        messages.success(request, f'Theme "{theme.name}" has been updated.')
        return redirect('theme-editor')
    
    # Get all themes for the theme selector
    themes = ThemeSettings.objects.all()
    
    context = {
        'theme': theme,
        'themes': themes,
    }
    
    return render(request, 'core/theme_editor.html', context)

@login_required
def accessibility_settings(request):
    """
    View for users to manage accessibility settings.
    """
    # Get the user's preferences, create if it doesn't exist
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update accessibility preferences based on form data
        
        # Text size and motion
        preferences.text_size = request.POST.get('text_size', preferences.text_size)
        preferences.motion_preference = request.POST.get('motion_preference', preferences.motion_preference)
        
        # Boolean fields
        preferences.high_contrast = 'high_contrast' in request.POST
        preferences.increase_text_spacing = 'increase_text_spacing' in request.POST
        preferences.dyslexia_friendly_font = 'dyslexia_friendly_font' in request.POST
        preferences.screen_reader_optimization = 'screen_reader_optimization' in request.POST
        preferences.keyboard_navigation_optimization = 'keyboard_navigation_optimization' in request.POST
        
        preferences.save()
        messages.success(request, 'Your accessibility settings have been updated.')
        return redirect('accessibility-settings')
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'core/accessibility_settings.html', context)

@login_required
@require_POST
def apply_theme(request):
    """
    AJAX endpoint to apply a theme to the user's preferences.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    theme_id = request.POST.get('theme_id')
    if not theme_id:
        return JsonResponse({'error': 'Theme ID is required'}, status=400)
    
    try:
        theme = ThemeSettings.objects.get(id=theme_id)
    except ThemeSettings.DoesNotExist:
        return JsonResponse({'error': 'Theme not found'}, status=404)
    
    # Get the user's preferences, create if it doesn't exist
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    # Update the user's preferences to use this theme's mode
    preferences.theme_mode = theme.theme_mode
    preferences.save()
    
    return JsonResponse({'status': 'success', 'message': f'Successfully applied the {theme.name} theme.'})

@login_required
@require_POST
def preview_theme(request):
    """
    AJAX endpoint to preview a theme without applying it.
    """
    theme_id = request.POST.get('theme_id')
    if not theme_id:
        return JsonResponse({'error': 'Theme ID is required'}, status=400)
    
    try:
        theme = ThemeSettings.objects.get(id=theme_id)
    except ThemeSettings.DoesNotExist:
        return JsonResponse({'error': 'Theme not found'}, status=404)
    
    # Store the theme ID in the session for preview
    request.session['theme_preview_id'] = str(theme.id)
    
    return JsonResponse({'status': 'success', 'message': f'Previewing the {theme.name} theme.'})

@login_required
@require_POST
def end_preview(request):
    """
    AJAX endpoint to end theme preview.
    """
    if 'theme_preview_id' in request.session:
        del request.session['theme_preview_id']
    
    return JsonResponse({'status': 'success', 'message': 'Theme preview ended.'})

@login_required
@require_POST
def reset_theme(request):
    """
    Reset the user's theme to the system default.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get the user's preferences, create if it doesn't exist
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    # Get the default theme
    default_theme = ThemeSettings.objects.filter(is_default=True).first()
    if not default_theme:
        default_theme = ThemeSettings.objects.first()
    
    if default_theme:
        # Reset to default theme mode
        preferences.theme_mode = default_theme.theme_mode
        # Reset custom color settings
        preferences.use_custom_colors = False
        preferences.primary_color = ''
        preferences.save()
    
    # Clear any theme preview
    if 'theme_preview_id' in request.session:
        del request.session['theme_preview_id']
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Theme reset to system default.'})
    else:
        messages.success(request, 'Your theme has been reset to the system default.')
        return redirect('core:theme_settings')