from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
import uuid

from courses.models import Course
from qr_codes.models import QRCode, QRCodeScan, QRCodeBatch
from qr_codes.serializers import (
    QRCodeSerializer, QRCodeCreateSerializer,
    QRCodeScanSerializer, QRCodeScanRequestSerializer, QRCodeScanResponseSerializer,
    QRCodeBatchSerializer, QRCodeBatchCreateSerializer
)

User = get_user_model()

class QRCodeSerializerTests(TestCase):
    """Tests for the QRCode serializers."""
    
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
    
    def test_qr_code_serializer(self):
        """Test QRCodeSerializer."""
        serializer = QRCodeSerializer(self.qr_code)
        data = serializer.data
        
        # Check basic fields
        self.assertEqual(data['id'], str(self.qr_code.id))
        self.assertEqual(data['is_active'], True)
        self.assertEqual(data['access_level'], 'public')
        self.assertEqual(data['object_id'], self.course.id)
        
        # Check content type field
        self.assertEqual(data['content_type']['app_label'], 'courses')
        self.assertEqual(data['content_type']['model'], 'course')
        
        # Check read-only computed fields
        self.assertEqual(data['scan_count'], 0)
        self.assertEqual(data['is_scannable'], True)
        self.assertEqual(data['is_expired'], False)
        self.assertEqual(data['is_scan_limit_reached'], False)
    
    def test_qr_code_create_serializer(self):
        """Test QRCodeCreateSerializer."""
        data = {
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'object_id': self.course.id,
            'is_active': True,
            'access_level': 'enrolled'
        }
        
        serializer = QRCodeCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        qr_code = serializer.save()
        self.assertEqual(qr_code.content_type, self.course_content_type)
        self.assertEqual(qr_code.object_id, self.course.id)
        self.assertEqual(qr_code.is_active, True)
        self.assertEqual(qr_code.access_level, 'enrolled')
    
    def test_qr_code_create_serializer_invalid_object(self):
        """Test QRCodeCreateSerializer with invalid object."""
        data = {
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'object_id': 9999,  # Non-existent object
            'is_active': True,
            'access_level': 'public'
        }
        
        serializer = QRCodeCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Object with id=9999 does not exist', str(serializer.errors))
    
    def test_qr_code_create_serializer_invalid_content_type(self):
        """Test QRCodeCreateSerializer with invalid content type."""
        data = {
            'content_type': {'app_label': 'invalid', 'model': 'invalid'},
            'object_id': 1,
            'is_active': True,
            'access_level': 'public'
        }
        
        serializer = QRCodeCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ContentType with app_label=invalid and model=invalid does not exist', 
                     str(serializer.errors))


class QRCodeScanSerializerTests(TestCase):
    """Tests for the QRCodeScan serializers."""
    
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
    
    def test_qr_code_scan_serializer(self):
        """Test QRCodeScanSerializer."""
        serializer = QRCodeScanSerializer(self.scan)
        data = serializer.data
        
        # Check basic fields
        self.assertEqual(data['id'], str(self.scan.id))
        self.assertEqual(str(data['qr_code']), str(self.qr_code.id))
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['ip_address'], '127.0.0.1')
        self.assertEqual(data['status'], 'success')
    
    def test_qr_code_scan_request_serializer(self):
        """Test QRCodeScanRequestSerializer."""
        data = {
            'qr_code_id': str(self.qr_code.id),
            'latitude': 37.7749,
            'longitude': -122.4194,
            'context_data': {'device': 'mobile', 'browser': 'chrome'}
        }
        
        serializer = QRCodeScanRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # Convert both to strings to ensure proper comparison (UUID objects vs string representation)
        self.assertEqual(str(serializer.validated_data['qr_code_id']), str(self.qr_code.id))
        self.assertEqual(serializer.validated_data['latitude'], 37.7749)
        self.assertEqual(serializer.validated_data['longitude'], -122.4194)
        self.assertEqual(serializer.validated_data['context_data'], 
                        {'device': 'mobile', 'browser': 'chrome'})
    
    def test_qr_code_scan_request_serializer_minimal(self):
        """Test QRCodeScanRequestSerializer with minimal data."""
        data = {
            'qr_code_id': str(self.qr_code.id)
        }
        
        serializer = QRCodeScanRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(str(serializer.validated_data['qr_code_id']), str(self.qr_code.id))
        self.assertEqual(serializer.validated_data['context_data'], {})
    
    def test_qr_code_scan_response_serializer(self):
        """Test QRCodeScanResponseSerializer."""
        data = {
            'success': True,
            'status': 'success',
            'message': 'QR code scanned successfully',
            'target_type': 'courses.course',
            'target_id': self.course.id,
            'target_url': '/courses/1/',
            'additional_data': {'course_title': 'Test Course'},
            'scan_id': str(uuid.uuid4())
        }
        
        serializer = QRCodeScanResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['success'], True)
        self.assertEqual(serializer.validated_data['status'], 'success')
        self.assertEqual(serializer.validated_data['message'], 'QR code scanned successfully')
        self.assertEqual(serializer.validated_data['target_type'], 'courses.course')
        self.assertEqual(serializer.validated_data['target_id'], self.course.id)
        self.assertEqual(serializer.validated_data['target_url'], '/courses/1/')
        self.assertEqual(serializer.validated_data['additional_data'], 
                        {'course_title': 'Test Course'})


class QRCodeBatchSerializerTests(TestCase):
    """Tests for the QRCodeBatch serializers."""
    
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
        
        # Create QR codes in the batch
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
        
        # Update batch counts
        self.batch.codes_count = 2
        self.batch.save()
    
    def test_qr_code_batch_serializer(self):
        """Test QRCodeBatchSerializer."""
        serializer = QRCodeBatchSerializer(self.batch)
        data = serializer.data
        
        # Check basic fields
        self.assertEqual(data['id'], str(self.batch.id))
        self.assertEqual(data['name'], 'Test Batch')
        self.assertEqual(data['description'], 'A test batch')
        self.assertEqual(data['target_type'], 'course')
        self.assertEqual(data['is_active'], True)
        self.assertEqual(data['access_level'], 'public')
        self.assertEqual(data['created_by'], self.user.id)
        
        # Check computed fields
        self.assertEqual(data['codes_count'], 2)
        self.assertEqual(data['scans_count'], 0)
        
        # Check content type field
        self.assertEqual(data['content_type']['app_label'], 'courses')
        self.assertEqual(data['content_type']['model'], 'course')
    
    def test_qr_code_batch_create_serializer(self):
        """Test QRCodeBatchCreateSerializer."""
        data = {
            'name': 'New Batch',
            'description': 'A new batch',
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'target_type': 'course',
            'is_active': True,
            'access_level': 'enrolled',
            'target_ids': [self.course.id]
        }
        
        serializer = QRCodeBatchCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Note: We don't test save() here because it requires request.user context
        # which is simpler to test in the viewset tests
    
    def test_qr_code_batch_create_serializer_without_content_type(self):
        """Test QRCodeBatchCreateSerializer without content type."""
        data = {
            'name': 'New Batch',
            'description': 'A new batch',
            'target_type': 'course',
            'is_active': True,
            'access_level': 'public'
        }
        
        serializer = QRCodeBatchCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_qr_code_batch_create_serializer_validation(self):
        """Test QRCodeBatchCreateSerializer validation."""
        # Missing content_type but with target_ids
        data = {
            'name': 'New Batch',
            'target_type': 'course',
            'target_ids': [self.course.id]
        }
        
        serializer = QRCodeBatchCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # Check that the content_type field has a validation error
        self.assertIn('content_type', serializer.errors)
        # Check that the error message is as expected
        self.assertIn('Content type is required when target IDs are provided', 
                    str(serializer.errors['content_type'][0]))