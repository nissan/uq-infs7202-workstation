from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import QRCode, QRCodeScan

class QRCodeService:
    @staticmethod
    def get_or_create_qr_code(obj, url):
        """Get or create a QR code for a given object."""
        content_type = ContentType.objects.get_for_model(obj)
        
        qr_code, created = QRCode.objects.get_or_create(
            content_type=content_type,
            object_id=obj.id,
            defaults={'url': url}
        )
        
        return qr_code
    
    @staticmethod
    def record_scan(qr_code, request=None):
        """Record a scan of a QR code."""
        # Update the QR code's last used time and scan count
        qr_code.last_used = timezone.now()
        qr_code.scan_count += 1
        qr_code.save()
        
        # Create a scan record
        scan = QRCodeScan.objects.create(
            qr_code=qr_code,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None
        )
        
        return scan
    
    @staticmethod
    def get_qr_codes_for_object(obj):
        """Get all QR codes for a given object."""
        content_type = ContentType.objects.get_for_model(obj)
        return QRCode.objects.filter(
            content_type=content_type,
            object_id=obj.id
        )
    
    @staticmethod
    def get_scan_stats(qr_code):
        """Get statistics for a QR code's scans."""
        scans = QRCodeScan.objects.filter(qr_code=qr_code)
        
        return {
            'total_scans': scans.count(),
            'unique_ips': scans.values('ip_address').distinct().count(),
            'first_scan': scans.order_by('scanned_at').first(),
            'last_scan': scans.order_by('-scanned_at').first(),
        } 