"""
Utility functions and mock objects for QR code testing.
"""
import uuid
import json
import base64
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from courses.models import Course, Module, Quiz
from qr_codes.models import QRCode, QRCodeScan, QRCodeBatch

User = get_user_model()

class MockQRGenerator:
    """Mock QR code generator for testing."""
    
    @staticmethod
    def generate_qr_image(qr_code_instance):
        """Generate a fake QR code image for testing."""
        # Create a simple base64 string as mock image data
        image_data = base64.b64encode(b'MOCK_QR_CODE_IMAGE').decode('utf-8')
        qr_code_instance.image_data = image_data
        qr_code_instance.save(update_fields=['image_data'])
        return image_data


class MockScanner:
    """Mock QR code scanner for testing."""
    
    def __init__(self, user=None):
        """Initialize with optional user."""
        self.user = user
        self.ip_address = '127.0.0.1'
        self.user_agent = 'MockScanner/1.0'
    
    def scan(self, qr_code_id):
        """Simulate scanning a QR code."""
        from qr_codes.services import QRCodeService
        
        # Validate the scan
        is_valid, message, qr_code = QRCodeService.validate_scan(
            qr_code_id, 
            user=self.user
        )
        
        if not is_valid:
            return {
                'success': False,
                'status': 'error',
                'message': message
            }
        
        # Record scan
        scan = QRCodeScan.objects.create(
            qr_code=qr_code,
            user=self.user,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            status='success'
        )
        
        # Update scan count
        qr_code.current_scans += 1
        qr_code.save()
        
        # Return success response
        return {
            'success': True,
            'status': 'success',
            'scan_id': str(scan.id),
            'target_type': f"{qr_code.content_type.app_label}.{qr_code.content_type.model}",
            'target_id': qr_code.object_id,
            'message': 'QR code scanned successfully'
        }


def create_test_qr_code(content_object, **kwargs):
    """Create a test QR code for any model instance."""
    content_type = ContentType.objects.get_for_model(content_object.__class__)
    
    defaults = {
        'is_active': True,
        'access_level': 'public',
        'payload': {},
    }
    defaults.update(kwargs)
    
    qr_code = QRCode.objects.create(
        content_type=content_type,
        object_id=content_object.id,
        **defaults
    )
    
    # Generate mock image data
    MockQRGenerator.generate_qr_image(qr_code)
    
    return qr_code


def create_test_batch(name, content_type_model, user, **kwargs):
    """Create a test batch of QR codes."""
    app_label, model = content_type_model.split('.')
    content_type = ContentType.objects.get(app_label=app_label, model=model)
    
    defaults = {
        'description': f'Test batch for {content_type_model}',
        'is_active': True,
        'access_level': 'public',
    }
    defaults.update(kwargs)
    
    batch = QRCodeBatch.objects.create(
        name=name,
        content_type=content_type,
        target_type=model,
        created_by=user,
        **defaults
    )
    
    return batch


def simulate_multiple_scans(qr_code, user, count=5):
    """Simulate multiple scans of a QR code."""
    scanner = MockScanner(user=user)
    results = []
    
    for _ in range(count):
        result = scanner.scan(qr_code.id)
        results.append(result)
    
    return results