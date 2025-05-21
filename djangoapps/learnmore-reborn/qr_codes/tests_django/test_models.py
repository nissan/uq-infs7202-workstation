from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

from courses.models import Course
from qr_codes.models import QRCode, QRCodeScan, QRCodeBatch

User = get_user_model()

class QRCodeModelTests(TestCase):
    """Tests for the QRCode model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            instructor=self.user
        )
        
        # Get content type for course
        self.course_content_type = ContentType.objects.get_for_model(Course)
        
        # Create a test QR code
        self.qr_code = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            is_active=True,
            access_level='public'
        )
    
    def test_qr_code_creation(self):
        """Test that a QR code can be created."""
        self.assertIsInstance(self.qr_code, QRCode)
        self.assertEqual(self.qr_code.content_type, self.course_content_type)
        self.assertEqual(self.qr_code.object_id, self.course.id)
        self.assertTrue(self.qr_code.is_active)
        self.assertEqual(self.qr_code.access_level, 'public')
        self.assertEqual(self.qr_code.current_scans, 0)
    
    def test_qr_code_str_method(self):
        """Test the string representation of a QR code."""
        expected_str = f"QR Code {self.qr_code.id} - course {self.course.id}"
        self.assertEqual(str(self.qr_code), expected_str)
    
    def test_qr_code_properties(self):
        """Test QR code properties."""
        # Test is_expired
        self.assertFalse(self.qr_code.is_expired)
        self.qr_code.expires_at = timezone.now() - timezone.timedelta(days=1)
        self.assertTrue(self.qr_code.is_expired)
        
        # Reset expiration
        self.qr_code.expires_at = None
        
        # Test is_scan_limit_reached
        self.assertFalse(self.qr_code.is_scan_limit_reached)
        self.qr_code.max_scans = 5
        self.qr_code.current_scans = 5
        self.assertTrue(self.qr_code.is_scan_limit_reached)
        
        # Reset scans
        self.qr_code.current_scans = 0
        
        # Test is_scannable
        self.assertTrue(self.qr_code.is_scannable)
        self.qr_code.is_active = False
        self.assertFalse(self.qr_code.is_scannable)


class QRCodeScanTests(TestCase):
    """Tests for the QRCodeScan model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            instructor=self.user
        )
        
        # Get content type for course
        self.course_content_type = ContentType.objects.get_for_model(Course)
        
        # Create a test QR code
        self.qr_code = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            is_active=True,
            access_level='public'
        )
        
        # Create a test scan
        self.scan = QRCodeScan.objects.create(
            qr_code=self.qr_code,
            user=self.user,
            ip_address='127.0.0.1',
            status='success'
        )
    
    def test_scan_creation(self):
        """Test that a scan can be created."""
        self.assertIsInstance(self.scan, QRCodeScan)
        self.assertEqual(self.scan.qr_code, self.qr_code)
        self.assertEqual(self.scan.user, self.user)
        self.assertEqual(self.scan.ip_address, '127.0.0.1')
        self.assertEqual(self.scan.status, 'success')
    
    def test_scan_str_method(self):
        """Test the string representation of a scan."""
        expected_str = f"Scan of {self.qr_code} at {self.scan.scanned_at}"
        self.assertEqual(str(self.scan), expected_str)


class QRCodeBatchTests(TestCase):
    """Tests for the QRCodeBatch model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            instructor=self.user
        )
        
        # Get content type for course
        self.course_content_type = ContentType.objects.get_for_model(Course)
        
        # Create a test batch
        self.batch = QRCodeBatch.objects.create(
            name='Test Batch',
            description='A test batch',
            created_by=self.user,
            content_type=self.course_content_type,
            target_type='course',
            is_active=True,
            access_level='public'
        )
        
        # Create test QR codes in the batch
        self.qr_code1 = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            is_active=True,
            access_level='public',
            batch=self.batch
        )
        
        self.qr_code2 = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            is_active=True,
            access_level='public',
            batch=self.batch
        )
    
    def test_batch_creation(self):
        """Test that a batch can be created."""
        self.assertIsInstance(self.batch, QRCodeBatch)
        self.assertEqual(self.batch.name, 'Test Batch')
        self.assertEqual(self.batch.created_by, self.user)
        self.assertEqual(self.batch.content_type, self.course_content_type)
        self.assertEqual(self.batch.target_type, 'course')
        self.assertTrue(self.batch.is_active)
    
    def test_batch_str_method(self):
        """Test the string representation of a batch."""
        expected_str = f"Batch: Test Batch (2 codes)"
        self.assertEqual(str(self.batch), expected_str)
    
    def test_get_active_codes(self):
        """Test getting active codes from a batch."""
        # Initially both codes are active
        active_codes = self.batch.get_active_codes()
        self.assertEqual(active_codes.count(), 2)
        
        # Deactivate one code
        self.qr_code1.is_active = False
        self.qr_code1.save()
        
        active_codes = self.batch.get_active_codes()
        self.assertEqual(active_codes.count(), 1)
        self.assertEqual(active_codes.first(), self.qr_code2)