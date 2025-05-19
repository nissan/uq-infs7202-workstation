from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json
import os
from PIL import Image
from io import BytesIO

from apps.courses.models import Course, Module, Content
from .models import QRCode, QRCodeScan
from .services import QRCodeService
from .views import scan_qr_code_redirect, QRCodeDetailView, qr_code_statistics, print_course_qr_codes

User = get_user_model()

class QRCodeModelTests(TestCase):
    """Test cases for QR Code models."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Get the content type for the course
        self.content_type = ContentType.objects.get_for_model(self.course)
        
        # Create a QR code
        self.qr_code = QRCode.objects.create(
            content_type=self.content_type,
            object_id=self.course.id,
            url='http://example.com/course/test-course'
        )
        
        # Create a QR code scan
        self.scan = QRCodeScan.objects.create(
            qr_code=self.qr_code,
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
    
    def test_qr_code_str_method(self):
        """Test the string representation of a QRCode."""
        self.assertEqual(str(self.qr_code), f"QR Code for {self.course}")
    
    def test_qr_code_scan_str_method(self):
        """Test the string representation of a QRCodeScan."""
        self.assertEqual(
            str(self.scan), 
            f"Scan of {self.qr_code} at {self.scan.scanned_at}"
        )
    
    def test_qr_code_generation(self):
        """Test that QR code images are generated."""
        self.assertIsNotNone(self.qr_code.code)
        
        # Check that the file exists
        self.assertTrue(os.path.exists(self.qr_code.code.path))
        
        # Check that it's a valid image
        try:
            img = Image.open(self.qr_code.code.path)
            self.assertTrue(isinstance(img, Image.Image))
        except Exception as e:
            self.fail(f"Failed to open QR code image: {e}")
    
    def test_qr_code_unique_constraint(self):
        """Test that QR codes must be unique for a content object."""
        # Attempt to create another QR code for the same course
        with self.assertRaises(Exception):
            QRCode.objects.create(
                content_type=self.content_type,
                object_id=self.course.id,
                url='http://example.com/course/test-course-2'
            )


class QRCodeServiceTests(TestCase):
    """Test cases for QRCodeService."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Get the content type for the course
        self.content_type = ContentType.objects.get_for_model(self.course)
        
        # Create request factory
        self.factory = RequestFactory()
    
    def test_get_or_create_qr_code(self):
        """Test getting or creating a QR code."""
        # Get or create a QR code
        qr_code = QRCodeService.get_or_create_qr_code(
            self.course, 
            'http://example.com/course/test-course'
        )
        
        # Check that the QR code was created
        self.assertIsNotNone(qr_code)
        self.assertEqual(qr_code.content_type, self.content_type)
        self.assertEqual(qr_code.object_id, self.course.id)
        self.assertEqual(qr_code.url, 'http://example.com/course/test-course')
        
        # Create another QR code for the same object
        qr_code2 = QRCodeService.get_or_create_qr_code(
            self.course, 
            'http://example.com/course/test-course'
        )
        
        # Check that we got the same QR code
        self.assertEqual(qr_code, qr_code2)
    
    def test_record_scan(self):
        """Test recording a QR code scan."""
        # Create a QR code
        qr_code = QRCodeService.get_or_create_qr_code(
            self.course, 
            'http://example.com/course/test-course'
        )
        
        # Record a scan with request
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        
        scan = QRCodeService.record_scan(qr_code, request)
        
        # Check that the scan was recorded
        self.assertEqual(scan.qr_code, qr_code)
        self.assertEqual(scan.ip_address, '127.0.0.1')
        self.assertEqual(scan.user_agent, 'Test User Agent')
        
        # Check that the QR code was updated
        qr_code.refresh_from_db()
        self.assertEqual(qr_code.scan_count, 1)
        self.assertIsNotNone(qr_code.last_used)
    
    def test_get_qr_codes_for_object(self):
        """Test getting QR codes for an object."""
        # Create a QR code
        qr_code = QRCodeService.get_or_create_qr_code(
            self.course, 
            'http://example.com/course/test-course'
        )
        
        # Get QR codes for the course
        qr_codes = QRCodeService.get_qr_codes_for_object(self.course)
        
        # Check that we got the QR code
        self.assertEqual(qr_codes.count(), 1)
        self.assertEqual(qr_codes.first(), qr_code)
    
    def test_get_scan_stats(self):
        """Test getting scan statistics for a QR code."""
        # Create a QR code
        qr_code = QRCodeService.get_or_create_qr_code(
            self.course, 
            'http://example.com/course/test-course'
        )
        
        # Record some scans
        for i in range(3):
            QRCodeScan.objects.create(
                qr_code=qr_code,
                ip_address=f'127.0.0.{i}',
                user_agent=f'Test User Agent {i}'
            )
        
        # Get scan stats
        stats = QRCodeService.get_scan_stats(qr_code)
        
        # Check the stats
        self.assertEqual(stats['total_scans'], 3)
        self.assertEqual(stats['unique_ips'], 3)


class QRCodeViewTests(TestCase):
    """Test cases for QR Code views."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a client and log in
        self.client = Client()
        self.client.login(username='testuser', password='password123')
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Create a module
        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
            order=1
        )
        
        # Get content types
        self.course_content_type = ContentType.objects.get_for_model(self.course)
        self.module_content_type = ContentType.objects.get_for_model(self.module)
        
        # Create QR codes
        self.course_qr_code = QRCode.objects.create(
            content_type=self.course_content_type,
            object_id=self.course.id,
            url='http://example.com/course/test-course'
        )
        
        self.module_qr_code = QRCode.objects.create(
            content_type=self.module_content_type,
            object_id=self.module.id,
            url='http://example.com/module/test-module'
        )
        
        # Create scans
        for i in range(5):
            QRCodeScan.objects.create(
                qr_code=self.course_qr_code,
                ip_address=f'127.0.0.{i}',
                user_agent=f'Test User Agent {i}'
            )
        
        for i in range(3):
            QRCodeScan.objects.create(
                qr_code=self.module_qr_code,
                ip_address=f'127.0.0.{i}',
                user_agent=f'Test User Agent {i}'
            )
        
        # Create request factory
        self.factory = RequestFactory()
    
    def test_scan_qr_code_redirect(self):
        """Test the QR code scan redirect view."""
        # Create a request
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        
        # Call the view
        response = scan_qr_code_redirect(request, self.course_qr_code.id)
        
        # Check the redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://example.com/course/test-course')
        
        # Check that the scan was recorded
        self.course_qr_code.refresh_from_db()
        self.assertEqual(self.course_qr_code.scan_count, 6)
    
    def test_qr_code_detail_view(self):
        """Test the QR code detail view."""
        # Create the URL
        url = reverse('qr_codes:qr_code_detail', args=[self.course_qr_code.id])
        
        # Get the response
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qr_codes/qr_code_detail.html')
        
        # Check the context
        self.assertEqual(response.context['qr_code'], self.course_qr_code)
        self.assertEqual(response.context['scan_stats']['total_scans'], 5)
    
    def test_qr_code_statistics_view(self):
        """Test the QR code statistics view."""
        # Create the URL
        url = reverse('qr_codes:statistics')
        
        # Get the response
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qr_codes/statistics.html')
        
        # Check the context
        self.assertEqual(response.context['total_scans'], 8)
        self.assertEqual(response.context['active_qr_codes'], 2)
        self.assertEqual(response.context['average_scans'], 4.0)
        self.assertEqual(len(response.context['top_qr_codes']), 2)
    
    @patch('weasyprint.HTML')
    def test_print_course_qr_codes(self, mock_weasyprint_html):
        """Test the print course QR codes view."""
        # Mock the weasyprint HTML
        mock_html = MagicMock()
        mock_pdf = b'PDF content'
        mock_html.write_pdf.return_value = mock_pdf
        mock_weasyprint_html.return_value = mock_html
        
        # Create the URL
        url = reverse('qr_codes:print_course_qr_codes', args=[self.course.id])
        
        # Get the response
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, mock_pdf)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Check that weasyprint was called
        mock_weasyprint_html.assert_called_once()
        mock_html.write_pdf.assert_called_once()


class QRCodeTemplateTagTests(TestCase):
    """Test cases for QR Code template tags."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            slug='test-course',
            created_by=self.user
        )
        
        # Get the content type for the course
        self.content_type = ContentType.objects.get_for_model(self.course)
        
        # Create a QR code
        self.qr_code = QRCode.objects.create(
            content_type=self.content_type,
            object_id=self.course.id,
            url='http://example.com/course/test-course'
        )
    
    def test_get_qr_code_tag(self):
        """Test the get_qr_code template tag."""
        from .templatetags.qr_code_tags import get_qr_code
        
        # Get the QR code
        qr_code = get_qr_code(self.course)
        
        # Check that we got the right QR code
        self.assertEqual(qr_code, self.qr_code)
    
    def test_get_qr_code_url_tag(self):
        """Test the get_qr_code_url template tag."""
        from .templatetags.qr_code_tags import get_qr_code_url
        
        # Get the QR code URL
        url = get_qr_code_url(self.course)
        
        # Check that we got the right URL
        self.assertEqual(url, self.qr_code.code.url)
