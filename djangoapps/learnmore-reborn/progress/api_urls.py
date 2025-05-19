from rest_framework.routers import DefaultRouter
from .api_views import ProgressViewSet

router = DefaultRouter()
router.register(r'', ProgressViewSet)

urlpatterns = router.urls