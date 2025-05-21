from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

User = get_user_model()

# Choices
ACCESS_LEVELS = [
    ('public', 'Public'),
    ('enrolled', 'Enrolled Users Only'),
    ('instructor', 'Instructors Only'),
    ('admin', 'Admins Only'),
]

SCAN_STATUSES = [
    ('success', 'Success'),
    ('expired', 'Expired'),
    ('exceeded', 'Usage Exceeded'),
    ('invalid', 'Invalid'),
    ('unauthorized', 'Unauthorized'),
]

class QRCode(models.Model):
    """Model to store QR code information."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Target information
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Configuration
    max_scans = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of scans allowed, or blank for unlimited")
    current_scans = models.PositiveIntegerField(default=0, help_text="Number of times this code has been scanned")
    is_active = models.BooleanField(default=True, help_text="Whether this QR code is active and can be scanned")
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public', help_text="Access level required to scan this code")
    
    # Data
    payload = models.JSONField(default=dict, help_text="Additional data to include in the QR code")
    image_data = models.TextField(blank=True, help_text="Base64 encoded QR code image data")
    
    # Batch relationship
    batch = models.ForeignKey('QRCodeBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='codes')
    
    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"QR Code {self.id} - {self.content_type.model} {self.object_id}"
    
    @property
    def scan_count(self):
        """Return the number of scans for this QR code."""
        return self.scans.count()
    
    @property
    def is_expired(self):
        """Check if the QR code has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_scan_limit_reached(self):
        """Check if the scan limit has been reached."""
        if not self.max_scans:
            return False
        return self.current_scans >= self.max_scans
    
    @property
    def is_scannable(self):
        """Check if this QR code can be scanned."""
        return self.is_active and not self.is_expired and not self.is_scan_limit_reached


class QRCodeScan(models.Model):
    """Model to track QR code scans."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='scans')
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    # Scanner information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Location data (optional)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Additional data
    context_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=SCAN_STATUSES, default='success')
    
    class Meta:
        verbose_name = "QR Code Scan"
        verbose_name_plural = "QR Code Scans"
        ordering = ['-scanned_at']
    
    def __str__(self):
        return f"Scan of {self.qr_code} at {self.scanned_at}"


class QRCodeBatch(models.Model):
    """Model for managing batches of QR codes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_qr_batches')
    
    # Target information
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_type = models.CharField(max_length=50, help_text="Type of target (course, module, quiz)")
    
    # Batch configuration
    expires_at = models.DateTimeField(null=True, blank=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public')
    max_scans_per_code = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Batch data
    codes_count = models.PositiveIntegerField(default=0, help_text="Number of codes in this batch")
    scans_count = models.PositiveIntegerField(default=0, help_text="Number of times codes in this batch have been scanned")
    metadata = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "QR Code Batch"
        verbose_name_plural = "QR Code Batches"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Batch: {self.name} ({self.codes_count} codes)"
    
    def get_active_codes(self):
        """Return all active codes in this batch."""
        from django.utils import timezone
        return QRCode.objects.filter(
            batch=self,
            is_active=True
        ).exclude(
            expires_at__lt=timezone.now()
        )