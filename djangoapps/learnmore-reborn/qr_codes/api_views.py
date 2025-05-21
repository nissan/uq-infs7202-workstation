from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import QRCode, QRCodeScan, QRCodeBatch
from .serializers import (
    QRCodeSerializer, QRCodeCreateSerializer,
    QRCodeScanSerializer, QRCodeScanRequestSerializer, QRCodeScanResponseSerializer,
    QRCodeBatchSerializer, QRCodeBatchCreateSerializer
)
from .services import QRCodeService


class QRCodeViewSet(viewsets.ModelViewSet):
    """ViewSet for QR code management."""
    queryset = QRCode.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return QRCodeCreateSerializer
        return QRCodeSerializer
    
    def perform_create(self, serializer):
        qr_code = serializer.save()
        # Generate QR code image
        QRCodeService.generate_qr_image(qr_code)
    
    @action(detail=True, methods=['get'])
    def regenerate(self, request, pk=None):
        """Regenerate the QR code image."""
        qr_code = self.get_object()
        QRCodeService.generate_qr_image(qr_code)
        return Response(QRCodeSerializer(qr_code).data)
    
    @action(detail=True, methods=['get'])
    def scans(self, request, pk=None):
        """Get all scans for a specific QR code."""
        qr_code = self.get_object()
        scans = qr_code.scans.all()
        page = self.paginate_queryset(scans)
        if page is not None:
            serializer = QRCodeScanSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = QRCodeScanSerializer(scans, many=True)
        return Response(serializer.data)


class QRCodeScanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for QR code scan history."""
    queryset = QRCodeScan.objects.all()
    serializer_class = QRCodeScanSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def scan(self, request):
        """Process a QR code scan."""
        serializer = QRCodeScanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        qr_code_id = serializer.validated_data['qr_code_id']
        
        try:
            qr_code = QRCode.objects.get(id=qr_code_id)
        except QRCode.DoesNotExist:
            return Response({
                'success': False,
                'status': 'invalid',
                'message': 'QR code not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if QR code is active
        if not qr_code.is_active:
            return Response({
                'success': False,
                'status': 'inactive',
                'message': 'QR code is inactive'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if QR code has expired
        if qr_code.is_expired:
            return Response({
                'success': False,
                'status': 'expired',
                'message': 'QR code has expired'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if scan limit reached
        if qr_code.is_scan_limit_reached:
            return Response({
                'success': False,
                'status': 'exceeded',
                'message': 'Scan limit reached'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create scan record
        scan = QRCodeScan.objects.create(
            qr_code=qr_code,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            latitude=serializer.validated_data.get('latitude'),
            longitude=serializer.validated_data.get('longitude'),
            context_data=serializer.validated_data.get('context_data', {}),
            status='success'
        )
        
        # Update scan count
        qr_code.current_scans += 1
        qr_code.save()
        
        # Update batch scan count if applicable
        if qr_code.batch:
            batch = qr_code.batch
            batch.scans_count += 1
            batch.save()
        
        # Determine target URL based on content type
        target_url = None
        content_type = qr_code.content_type
        target_app = content_type.app_label
        target_model = content_type.model
        
        # Example URL mapping (customize as needed)
        url_mapping = {
            'courses': {
                'course': 'course-detail',
                'module': 'module-detail',
                'quiz': 'quiz-detail',
            }
        }
        
        if target_app in url_mapping and target_model in url_mapping[target_app]:
            url_name = url_mapping[target_app][target_model]
            target_url = reverse(url_name, kwargs={'pk': qr_code.object_id})
        
        # Return scan result
        response_data = {
            'success': True,
            'status': 'success',
            'message': 'QR code scanned successfully',
            'target_type': f"{content_type.app_label}.{content_type.model}",
            'target_id': qr_code.object_id,
            'target_url': target_url,
            'additional_data': qr_code.payload,
            'scan_id': scan.id
        }
        
        response_serializer = QRCodeScanResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            # This should not happen but just in case
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRCodeBatchViewSet(viewsets.ModelViewSet):
    """ViewSet for QR code batch management."""
    queryset = QRCodeBatch.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return QRCodeBatchCreateSerializer
        return QRCodeBatchSerializer
    
    def perform_create(self, serializer):
        # Save batch
        batch = serializer.save(created_by=self.request.user)
        
        # Create QR codes for targets if specified
        target_ids = serializer.validated_data.get('target_ids', [])
        if target_ids and batch.content_type:
            QRCodeService.create_batch_codes(
                batch=batch,
                target_ids=target_ids,
                content_type=batch.content_type,
                expires_at=batch.expires_at,
                max_scans=batch.max_scans_per_code,
                access_level=batch.access_level
            )
    
    @action(detail=True, methods=['post'])
    def generate_codes(self, request, pk=None):
        """Generate QR codes for a batch."""
        batch = self.get_object()
        
        # Validate request data
        if not batch.content_type:
            return Response({
                'error': 'Batch does not have a content type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        target_ids = request.data.get('target_ids', [])
        if not target_ids:
            return Response({
                'error': 'No target IDs specified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create QR codes
        created_codes = QRCodeService.create_batch_codes(
            batch=batch,
            target_ids=target_ids,
            content_type=batch.content_type,
            expires_at=batch.expires_at,
            max_scans=batch.max_scans_per_code,
            access_level=batch.access_level
        )
        
        return Response({
            'success': True,
            'message': f'Created {len(created_codes)} QR codes',
            'codes': QRCodeSerializer(created_codes, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def codes(self, request, pk=None):
        """Get all QR codes for a specific batch."""
        batch = self.get_object()
        codes = batch.codes.all()
        page = self.paginate_queryset(codes)
        if page is not None:
            serializer = QRCodeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = QRCodeSerializer(codes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a batch."""
        batch = self.get_object()
        total_codes = batch.codes.count()
        active_codes = batch.codes.filter(is_active=True).count()
        expired_codes = batch.codes.filter(expires_at__lt=timezone.now()).count()
        scanned_codes = batch.codes.filter(current_scans__gt=0).count()
        
        # Aggregate scans by date
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        scans_by_date = QRCodeScan.objects.filter(
            qr_code__batch=batch
        ).annotate(
            date=TruncDate('scanned_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return Response({
            'total_codes': total_codes,
            'active_codes': active_codes,
            'expired_codes': expired_codes,
            'scanned_codes': scanned_codes,
            'total_scans': batch.scans_count,
            'scans_by_date': list(scans_by_date)
        })