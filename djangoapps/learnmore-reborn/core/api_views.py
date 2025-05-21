from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings

from .models import ThemeSettings, UserPreferences, AccessibilityElement
from .serializers import (
    ThemeSettingsSerializer, UserPreferencesSerializer, 
    AccessibilityElementSerializer, AltTextSerializer,
    NavigationPreferencesSerializer, ThemePreferencesSerializer
)

User = get_user_model()

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read-only access is allowed for all users.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ThemeSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for theme settings.
    
    Allows viewing and editing theme settings. Only admins can create/edit themes,
    but any authenticated user can view them.
    """
    queryset = ThemeSettings.objects.all()
    serializer_class = ThemeSettingsSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get the default theme settings."""
        try:
            theme = ThemeSettings.objects.get(is_default=True)
        except ThemeSettings.DoesNotExist:
            # If no default theme, return the first theme
            theme = ThemeSettings.objects.first()
            if theme is None:
                return Response({'error': 'No theme settings available'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(theme)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this theme as the default."""
        if not request.user.is_staff:
            return Response({'error': 'Only staff members can change the default theme'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        theme = self.get_object()
        theme.is_default = True
        theme.save()
        
        serializer = self.get_serializer(theme)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview this theme without changing user preferences."""
        theme = self.get_object()
        # Store the theme ID in the session
        request.session['theme_preview_id'] = str(theme.id)
        return Response({'status': 'preview activated'})
    
    @action(detail=False, methods=['post'])
    def end_preview(self, request):
        """End theme preview."""
        if 'theme_preview_id' in request.session:
            del request.session['theme_preview_id']
        return Response({'status': 'preview deactivated'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active theme for the user."""
        # Check if there's a preview theme
        preview_id = request.session.get('theme_preview_id')
        if preview_id:
            try:
                theme = ThemeSettings.objects.get(id=preview_id)
                serializer = self.get_serializer(theme)
                data = serializer.data
                data['is_preview'] = True
                return Response(data)
            except ThemeSettings.DoesNotExist:
                # If the preview theme doesn't exist, remove it from the session
                del request.session['theme_preview_id']
        
        # If the user is authenticated, check their preferences
        if request.user.is_authenticated:
            try:
                preferences = UserPreferences.objects.get(user=request.user)
                
                # If the user has chosen a theme mode, use it
                if preferences.theme_mode != 'system':
                    theme_mode = preferences.theme_mode
                    theme = ThemeSettings.objects.filter(theme_mode=theme_mode).first()
                    if theme:
                        serializer = self.get_serializer(theme)
                        return Response(serializer.data)
            except UserPreferences.DoesNotExist:
                pass
        
        # Default to the default theme
        try:
            theme = ThemeSettings.objects.get(is_default=True)
        except ThemeSettings.DoesNotExist:
            theme = ThemeSettings.objects.first()
            if theme is None:
                return Response({'error': 'No theme settings available'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(theme)
        return Response(serializer.data)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user preferences.
    
    Allows users to view and edit their own preferences.
    Admins can view all user preferences but can only edit their own.
    """
    serializer_class = UserPreferencesSerializer
    
    def get_queryset(self):
        """Return appropriate queryset based on user permissions."""
        if self.request.user.is_staff:
            return UserPreferences.objects.all()
        return UserPreferences.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the user preferences object."""
        # If a specific ID is provided, use standard get_object logic
        if self.kwargs.get('pk'):
            obj = super().get_object()
            
            # Only admins can view other users' preferences
            if obj.user != self.request.user and not self.request.user.is_staff:
                self.permission_denied(self.request)
            
            # Only users can edit their own preferences
            if self.request.method not in permissions.SAFE_METHODS and obj.user != self.request.user:
                self.permission_denied(self.request, message="You cannot edit another user's preferences")
            
            return obj
        
        # If no ID provided, get/create the current user's preferences
        user_preferences, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return user_preferences
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current user's preferences."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_theme(self, request):
        """Update the current user's theme preferences."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        serializer = ThemePreferencesSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update the preferences
            for key, value in serializer.validated_data.items():
                setattr(preferences, key, value)
            
            preferences.updated_at = timezone.now()
            preferences.save()
            
            # Return the updated preferences
            response_serializer = self.get_serializer(preferences)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'])
    def update_navigation(self, request):
        """Update the current user's navigation preferences."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        serializer = NavigationPreferencesSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update the preferences
            preferences.simplified_navigation = serializer.validated_data.get('simplified_navigation', 
                                                               preferences.simplified_navigation)
            
            preferences.show_content_outlines = serializer.validated_data.get('show_content_outlines', 
                                                                preferences.show_content_outlines)
            
            # Additional navigation-related fields can be added to the model later if needed
            
            preferences.updated_at = timezone.now()
            preferences.save()
            
            # Return the updated preferences
            response_serializer = self.get_serializer(preferences)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessibilityElementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for accessibility elements.
    
    Allows admins to manage accessibility elements.
    Regular users can only view them.
    """
    queryset = AccessibilityElement.objects.all()
    serializer_class = AccessibilityElementSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def by_element_type(self, request):
        """Get accessibility elements filtered by type."""
        element_type = request.query_params.get('type')
        if not element_type:
            return Response({'error': 'Element type parameter is required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        elements = self.queryset.filter(element_type=element_type)
        page = self.paginate_queryset(elements)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(elements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def skip_targets(self, request):
        """Get all skip link targets."""
        elements = self.queryset.filter(is_skip_target=True)
        serializer = self.get_serializer(elements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_alt_text(self, request):
        """Update alt text for an element."""
        if not request.user.is_staff:
            return Response({'error': 'Only staff members can update alt text'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        serializer = AltTextSerializer(data=request.data)
        if serializer.is_valid():
            # In a real implementation, this would update the alt text in the database
            # For now, just return a success message
            return Response({'status': 'alt text updated'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_css_variables(request):
    """
    Get CSS variables for the current active theme.
    
    This endpoint returns CSS variables for direct usage in the frontend.
    It takes into account the user's preferences and any preview theme.
    """
    theme = None
    
    # Check if there's a preview theme
    preview_id = request.session.get('theme_preview_id')
    if preview_id:
        try:
            theme = ThemeSettings.objects.get(id=preview_id)
        except ThemeSettings.DoesNotExist:
            # If the preview theme doesn't exist, remove it from the session
            if 'theme_preview_id' in request.session:
                del request.session['theme_preview_id']
    
    # If no preview theme, check user preferences
    if not theme and request.user.is_authenticated:
        try:
            preferences = UserPreferences.objects.get(user=request.user)
            
            # If the user has custom colors, use them
            if preferences.use_custom_colors:
                # Create a custom theme dict based on user preferences
                css_vars = {
                    '--primary-color': preferences.primary_color or '#007bff',
                    # Add other custom colors from preferences
                }
                
                # Add theme mode specific variables
                if preferences.theme_mode == 'dark':
                    css_vars.update({
                        '--background-color': '#121212',
                        '--text-color': '#e0e0e0',
                        # Add other dark mode specific variables
                    })
                else:
                    css_vars.update({
                        '--background-color': '#ffffff',
                        '--text-color': '#212529',
                        # Add other light mode specific variables
                    })
                
                # Add accessibility variables
                if preferences.high_contrast:
                    css_vars.update({
                        '--contrast-ratio': '7',
                        # Add other high contrast variables
                    })
                
                if preferences.increase_text_spacing:
                    css_vars.update({
                        '--letter-spacing': '0.05em',
                        '--word-spacing': '0.1em',
                        '--line-height': '1.8',
                    })
                
                # Return the custom theme
                return JsonResponse({'cssVariables': css_vars})
            
            # If the user has chosen a theme mode, find an appropriate theme
            elif preferences.theme_mode != 'system':
                theme_mode = preferences.theme_mode
                theme = ThemeSettings.objects.filter(theme_mode=theme_mode).first()
        except UserPreferences.DoesNotExist:
            pass
    
    # If still no theme, use the default
    if not theme:
        try:
            theme = ThemeSettings.objects.get(is_default=True)
        except ThemeSettings.DoesNotExist:
            theme = ThemeSettings.objects.first()
    
    # If there's no theme at all, return default values
    if not theme:
        return JsonResponse({
            'cssVariables': {
                '--primary-color': '#007bff',
                '--secondary-color': '#6c757d',
                '--success-color': '#28a745',
                '--danger-color': '#dc3545',
                '--warning-color': '#ffc107',
                '--info-color': '#17a2b8',
                '--background-color': '#ffffff',
                '--text-color': '#212529',
                '--border-radius': '0.25rem',
                '--spacing-unit': '1rem',
                '--font-family': 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
                '--base-font-size': '16px',
            }
        })
    
    # Convert theme object to CSS variables
    css_vars = {
        '--primary-color': theme.primary_color,
        '--secondary-color': theme.secondary_color,
        '--success-color': theme.success_color,
        '--danger-color': theme.danger_color,
        '--warning-color': theme.warning_color,
        '--info-color': theme.info_color,
        '--background-color': theme.background_color,
        '--text-color': theme.text_color,
        '--border-radius': theme.border_radius,
        '--spacing-unit': theme.spacing_unit,
        '--font-family': theme.font_family,
        '--base-font-size': theme.base_font_size,
        '--heading-font-family': theme.heading_font_family or theme.font_family,
        '--container-max-width': theme.container_max_width,
    }
    
    # Add accessibility variables if the user has them set
    if request.user.is_authenticated:
        try:
            preferences = UserPreferences.objects.get(user=request.user)
            
            if preferences.high_contrast:
                css_vars.update({
                    '--contrast-ratio': '7',
                    # Add other high contrast variables
                })
            
            if preferences.increase_text_spacing:
                css_vars.update({
                    '--letter-spacing': '0.05em',
                    '--word-spacing': '0.1em',
                    '--line-height': '1.8',
                })
            
            if preferences.dyslexia_friendly_font:
                css_vars['--font-family'] = '"OpenDyslexic", sans-serif'
            
            # Adjust text size
            if preferences.text_size == 'larger':
                css_vars['--base-font-size'] = '18px'
            elif preferences.text_size == 'largest':
                css_vars['--base-font-size'] = '20px'
            
        except UserPreferences.DoesNotExist:
            pass
    
    return JsonResponse({'cssVariables': css_vars})