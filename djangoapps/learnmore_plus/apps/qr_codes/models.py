from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

class QRCode(models.Model):
    """Model for storing QR codes for various content types."""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    scan_count = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['content_type', 'object_id']
    
    def __str__(self):
        return f"QR Code for {self.content_object}"
    
    def generate_qr_code(self):
        """Generate QR code image and save it."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to a BytesIO object
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Save the image to the model
        filename = f'qr_code_{self.content_type.model}_{self.object_id}.png'
        self.code.save(filename, File(buffer), save=False)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

class QRCodeScan(models.Model):
    """Model for tracking QR code scans."""
    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='scans')
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['qr_code', 'scanned_at']),
        ]
    
    def __str__(self):
        return f"Scan of {self.qr_code} at {self.scanned_at}"
