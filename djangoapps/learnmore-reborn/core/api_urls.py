from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'core_api'

router = DefaultRouter()
router.register(r'themes', api_views.ThemeSettingsViewSet)
router.register(r'preferences', api_views.UserPreferencesViewSet, basename='preferences')
router.register(r'accessibility', api_views.AccessibilityElementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('theme/default/', api_views.ThemeSettingsViewSet.as_view({'get': 'default'}), name='default-theme'),
    path('theme/preview/<int:pk>/', api_views.ThemeSettingsViewSet.as_view({'post': 'preview'}), name='preview-theme'),
    path('theme/apply/<int:pk>/', api_views.ThemeSettingsViewSet.as_view({'post': 'apply'}), name='apply-theme'),
    path('theme/reset/', api_views.ThemeSettingsViewSet.as_view({'post': 'reset'}), name='reset-theme'),
    path('css-variables/', api_views.get_css_variables, name='css-variables'),
]