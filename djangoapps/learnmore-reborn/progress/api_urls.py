from rest_framework.routers import DefaultRouter
from .api_views import ProgressViewSet

router = DefaultRouter()
router.register(r'', ProgressViewSet, basename='progress')

urlpatterns = router.urls