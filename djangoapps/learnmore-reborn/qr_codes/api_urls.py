from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import QRCodeViewSet, QRCodeScanViewSet, QRCodeBatchViewSet

router = DefaultRouter()
router.register(r'codes', QRCodeViewSet)
router.register(r'scans', QRCodeScanViewSet)
router.register(r'batches', QRCodeBatchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]