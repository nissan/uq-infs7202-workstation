from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status
import json
import uuid

from courses.models import Course
from qr_codes.models import QRCode, QRCodeScan, QRCodeBatch
from qr_codes.services import QRCodeService

User = get_user_model()

class QRCodeAPITests(TestCase):
    """Tests for the QRCode API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            instructor=self.admin_user
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
        
        # Set up API client
        self.client = APIClient()
        
        # API URLs
        self.qr_codes_url = reverse('qrcode-list')
        self.qr_code_detail_url = reverse('qrcode-detail', args=[self.qr_code.id])
        self.qr_code_regenerate_url = reverse('qrcode-regenerate', args=[self.qr_code.id])
        self.qr_code_scans_url = reverse('qrcode-scans', args=[self.qr_code.id])
    
    def test_list_qr_codes_authenticated(self):
        """Test that authenticated users can list QR codes."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.qr_codes_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(str(response.data['results'][0]['id']), str(self.qr_code.id))
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 1)
            self.assertEqual(str(response.data[0]['id']), str(self.qr_code.id))
    
    def test_list_qr_codes_unauthenticated(self):
        """Test that unauthenticated users cannot list QR codes."""
        response = self.client.get(self.qr_codes_url)
        # Accept either 401 UNAUTHORIZED or 403 FORBIDDEN
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_create_qr_code(self):
        """Test creating a QR code."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'object_id': self.course.id,
            'is_active': True,
            'access_level': 'enrolled'
        }
        
        response = self.client.post(self.qr_codes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Ensure response.data has the expected structure
        self.assertIn('id', response.data, f"Response data missing 'id' key: {response.data}")
        
        # Check the created QR code
        qr_code = QRCode.objects.get(id=response.data['id'])
        self.assertEqual(qr_code.content_type, self.course_content_type)
        self.assertEqual(qr_code.object_id, self.course.id)
        self.assertEqual(qr_code.is_active, True)
        self.assertEqual(qr_code.access_level, 'enrolled')
        
        # Check that the image was generated
        self.assertIsNotNone(qr_code.image_data)
    
    def test_retrieve_qr_code(self):
        """Test retrieving a QR code."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.qr_code_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['id']), str(self.qr_code.id))
        self.assertEqual(response.data['object_id'], self.course.id)
        self.assertEqual(response.data['is_active'], True)
    
    def test_update_qr_code(self):
        """Test updating a QR code."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'object_id': self.course.id,
            'is_active': False,
            'access_level': 'instructor'
        }
        
        response = self.client.put(self.qr_code_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check the updated QR code
        self.qr_code.refresh_from_db()
        self.assertEqual(self.qr_code.is_active, False)
        self.assertEqual(self.qr_code.access_level, 'instructor')
    
    def test_delete_qr_code(self):
        """Test deleting a QR code."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.qr_code_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(QRCode.objects.filter(id=self.qr_code.id).exists())
    
    def test_regenerate_qr_code(self):
        """Test regenerating a QR code image."""
        self.client.force_authenticate(user=self.admin_user)
        
        # First, ensure the QR code has no image
        self.qr_code.image_data = ''
        self.qr_code.save()
        
        response = self.client.get(self.qr_code_regenerate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the image was generated
        self.qr_code.refresh_from_db()
        self.assertIsNotNone(self.qr_code.image_data)
        self.assertTrue(len(self.qr_code.image_data) > 0)
    
    def test_get_qr_code_scans(self):
        """Test getting scans for a QR code."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create some test scans
        scan1 = QRCodeScan.objects.create(
            qr_code=self.qr_code,
            user=self.admin_user,
            ip_address='127.0.0.1',
            status='success'
        )
        
        scan2 = QRCodeScan.objects.create(
            qr_code=self.qr_code,
            user=self.regular_user,
            ip_address='127.0.0.2',
            status='success'
        )
        
        response = self.client.get(self.qr_code_scans_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 2)
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 2)


class QRCodeScanAPITests(TestCase):
    """Tests for the QRCodeScan API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword'
        )
        
        # Create a test course
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            instructor=self.admin_user
        )
        
        # Get content type for course
        self.course_content_type = ContentType.objects.get_for_model(Course)
        
        # Create test QR codes
        self.active_qr_code = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            is_active=True,
            access_level='public'
        )
        
        self.inactive_qr_code = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            is_active=False,
            access_level='public'
        )
        
        # Set up API client
        self.client = APIClient()
        
        # API URLs
        self.scans_url = reverse('qrcodescan-list')
        self.scan_url = reverse('qrcodescan-scan')
    
    def test_list_scans_authenticated(self):
        """Test that authenticated users can list scans."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.scans_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 0)  # No scans yet
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 0)  # No scans yet
    
    def test_list_scans_unauthenticated(self):
        """Test that unauthenticated users cannot list scans."""
        response = self.client.get(self.scans_url)
        # Accept either 401 UNAUTHORIZED or 403 FORBIDDEN
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_process_scan_active_qr_code(self):
        """Test processing a scan for an active QR code."""
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'qr_code_id': str(self.active_qr_code.id),
            'latitude': 37.7749,
            'longitude': -122.4194,
            'context_data': {'device': 'test'}
        }
        
        response = self.client.post(self.scan_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['target_type'], 'courses.course')
        self.assertEqual(response.data['target_id'], self.course.id)
        
        # Check that a scan was created
        self.assertEqual(QRCodeScan.objects.count(), 1)
        scan = QRCodeScan.objects.first()
        self.assertEqual(scan.qr_code, self.active_qr_code)
        self.assertEqual(scan.user, self.regular_user)
        self.assertEqual(scan.status, 'success')
        
        # Check that the scan count was updated
        self.active_qr_code.refresh_from_db()
        self.assertEqual(self.active_qr_code.current_scans, 1)
    
    def test_process_scan_inactive_qr_code(self):
        """Test processing a scan for an inactive QR code."""
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'qr_code_id': str(self.inactive_qr_code.id)
        }
        
        response = self.client.post(self.scan_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['status'], 'inactive')
        
        # Check that no scan was created
        self.assertEqual(QRCodeScan.objects.count(), 0)
    
    def test_process_scan_nonexistent_qr_code(self):
        """Test processing a scan for a non-existent QR code."""
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'qr_code_id': str(uuid.uuid4())  # Random UUID
        }
        
        response = self.client.post(self.scan_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['status'], 'invalid')
        
        # Check that no scan was created
        self.assertEqual(QRCodeScan.objects.count(), 0)


class QRCodeBatchAPITests(TestCase):
    """Tests for the QRCodeBatch API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword'
        )
        
        # Create test courses
        self.course1 = Course.objects.create(
            title='Test Course 1',
            description='A test course',
            instructor=self.admin_user
        )
        
        self.course2 = Course.objects.create(
            title='Test Course 2',
            description='Another test course',
            instructor=self.admin_user
        )
        
        # Get content type for course
        self.course_content_type = ContentType.objects.get_for_model(Course)
        
        # Create a test batch
        self.batch = QRCodeBatch.objects.create(
            name='Test Batch',
            description='A test batch',
            created_by=self.admin_user,
            content_type=self.course_content_type,
            target_type='course',
            is_active=True,
            access_level='public'
        )
        
        # Create QR codes in the batch
        self.qr_code1 = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course1.id,
            is_active=True,
            access_level='public',
            batch=self.batch
        )
        
        self.qr_code2 = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course2.id,
            is_active=True,
            access_level='public',
            batch=self.batch
        )
        
        # Update batch counts
        self.batch.codes_count = 2
        self.batch.save()
        
        # Set up API client
        self.client = APIClient()
        
        # API URLs
        self.batches_url = reverse('qrcodebatch-list')
        self.batch_detail_url = reverse('qrcodebatch-detail', args=[self.batch.id])
        self.batch_codes_url = reverse('qrcodebatch-codes', args=[self.batch.id])
        self.batch_stats_url = reverse('qrcodebatch-stats', args=[self.batch.id])
        self.batch_generate_codes_url = reverse('qrcodebatch-generate-codes', args=[self.batch.id])
    
    def test_list_batches_authenticated(self):
        """Test that authenticated users can list batches."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.batches_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(str(response.data['results'][0]['id']), str(self.batch.id))
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 1)
            self.assertEqual(str(response.data[0]['id']), str(self.batch.id))
    
    def test_list_batches_unauthenticated(self):
        """Test that unauthenticated users cannot list batches."""
        response = self.client.get(self.batches_url)
        # Accept either 401 UNAUTHORIZED or 403 FORBIDDEN
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_create_batch(self):
        """Test creating a batch."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'name': 'New Batch',
            'description': 'A new batch',
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'target_type': 'course',
            'is_active': True,
            'access_level': 'enrolled'
        }
        
        response = self.client.post(self.batches_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check the created batch
        batch = QRCodeBatch.objects.get(id=response.data['id'])
        self.assertEqual(batch.name, 'New Batch')
        self.assertEqual(batch.description, 'A new batch')
        self.assertEqual(batch.content_type, self.course_content_type)
        self.assertEqual(batch.target_type, 'course')
        self.assertEqual(batch.is_active, True)
        self.assertEqual(batch.access_level, 'enrolled')
        self.assertEqual(batch.created_by, self.admin_user)
    
    def test_create_batch_with_target_ids(self):
        """Test creating a batch with target IDs."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'name': 'New Batch with Targets',
            'description': 'A new batch with target IDs',
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'target_type': 'course',
            'is_active': True,
            'access_level': 'public',
            'target_ids': [self.course1.id, self.course2.id]
        }
        
        response = self.client.post(self.batches_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that QR codes were created
        batch = QRCodeBatch.objects.get(id=response.data['id'])
        self.assertEqual(batch.codes.count(), 2)
    
    def test_retrieve_batch(self):
        """Test retrieving a batch."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.batch_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['id']), str(self.batch.id))
        self.assertEqual(response.data['name'], 'Test Batch')
        self.assertEqual(response.data['codes_count'], 2)
    
    def test_update_batch(self):
        """Test updating a batch."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'name': 'Updated Batch',
            'description': 'Updated description',
            'content_type': {'app_label': 'courses', 'model': 'course'},
            'target_type': 'course',
            'is_active': False,
            'access_level': 'instructor'
        }
        
        response = self.client.put(self.batch_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check the updated batch
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.name, 'Updated Batch')
        self.assertEqual(self.batch.description, 'Updated description')
        self.assertEqual(self.batch.is_active, False)
        self.assertEqual(self.batch.access_level, 'instructor')
    
    def test_delete_batch(self):
        """Test deleting a batch."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.batch_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(QRCodeBatch.objects.filter(id=self.batch.id).exists())
    
    def test_get_batch_codes(self):
        """Test getting QR codes for a batch."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.batch_codes_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 2)
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 2)
    
    def test_get_batch_stats(self):
        """Test getting statistics for a batch."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.batch_stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_codes'], 2)
        self.assertEqual(response.data['active_codes'], 2)
        self.assertEqual(response.data['expired_codes'], 0)
        self.assertEqual(response.data['scanned_codes'], 0)
        self.assertEqual(response.data['total_scans'], 0)
    
    def test_generate_codes(self):
        """Test generating QR codes for a batch."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create a new batch without codes
        new_batch = QRCodeBatch.objects.create(
            name='Empty Batch',
            description='A batch without codes',
            created_by=self.admin_user,
            content_type=self.course_content_type,
            target_type='course',
            is_active=True,
            access_level='public'
        )
        
        generate_url = reverse('qrcodebatch-generate-codes', args=[new_batch.id])
        
        data = {
            'target_ids': [self.course1.id, self.course2.id]
        }
        
        response = self.client.post(generate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['codes']), 2)
        
        # Check that codes were created
        new_batch.refresh_from_db()
        self.assertEqual(new_batch.codes.count(), 2)