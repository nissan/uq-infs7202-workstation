from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProgressViewSet, ModuleProgressViewSet

router = DefaultRouter()
router.register(r'progress', ProgressViewSet, basename='progress')
router.register(r'module-progress', ModuleProgressViewSet, basename='module-progress')

urlpatterns = router.urls