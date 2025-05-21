from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('settings/', views.theme_settings, name='theme_settings'),
    path('preferences/', views.user_preferences, name='user_preferences'),
    path('theme-editor/', views.theme_editor, name='theme_editor'),
    path('accessibility/', views.accessibility_settings, name='accessibility_settings'),
    path('preview-theme/<int:theme_id>/', views.preview_theme, name='preview_theme'),
    path('apply-theme/<int:theme_id>/', views.apply_theme, name='apply_theme'),
    path('reset-theme/', views.reset_theme, name='reset_theme'),
]