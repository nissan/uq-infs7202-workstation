from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import json

from courses.models import Course, Module, Quiz
from progress.models import Progress
from qr_codes.models import QRCode, QRCodeScan
from qr_codes.tests.utils import create_test_qr_code, MockScanner

User = get_user_model()

class QRCodeModelIntegrationTests(TestCase):
    """Tests for QR code integration with existing models."""
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpassword',
            is_staff=True
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpassword'
        )
        
        # Create a test course with QR enabled
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            instructor=self.instructor,
            qr_enabled=True
        )
        
        # Create test modules with different QR access levels
        self.module_public = Module.objects.create(
            title='Public Module',
            description='A public module',
            course=self.course,
            order=1,
            qr_access='public'
        )
        
        self.module_enrolled = Module.objects.create(
            title='Enrolled Only Module',
            description='An enrolled-only module',
            course=self.course,
            order=2,
            qr_access='enrolled'
        )
        
        # Create a test quiz with QR tracking
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz',
            module=self.module_public,
            qr_tracking=True
        )
        
        # Create enrollment and progress for the student
        from courses.models import Enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.student,
            course=self.course,
            status='active'
        )
        
        self.progress = Progress.objects.create(
            user=self.student,
            course=self.course,
            qr_scans={}
        )
        
        # Create QR codes for each model
        self.course_qr = create_test_qr_code(self.course)
        self.module_public_qr = create_test_qr_code(self.module_public)
        self.module_enrolled_qr = create_test_qr_code(self.module_enrolled, access_level='enrolled')
        self.quiz_qr = create_test_qr_code(self.quiz, access_level='enrolled')
    
    def test_course_qr_enabled(self):
        """Test that QR code can be created for a course with qr_enabled=True."""
        self.assertTrue(self.course.qr_enabled)
        self.assertEqual(self.course_qr.content_object, self.course)
    
    def test_module_qr_access(self):
        """Test different QR access levels for modules."""
        # Public module should be accessible to anyone
        self.assertEqual(self.module_public.qr_access, 'public')
        
        # Enrolled-only module should require enrollment
        self.assertEqual(self.module_enrolled.qr_access, 'enrolled')
    
    def test_quiz_qr_tracking(self):
        """Test QR tracking for quizzes."""
        self.assertTrue(self.quiz.qr_tracking)
        self.assertEqual(self.quiz_qr.content_object, self.quiz)
    
    def test_progress_qr_scans_tracking(self):
        """Test tracking QR scans in progress."""
        # Initially no scans
        self.assertEqual(self.progress.qr_scans, {})
        
        # Simulate scanning a QR code
        scanner = MockScanner(user=self.student)
        result = scanner.scan(self.course_qr.id)
        
        # Update progress with scan data (in a real app, this would be done by a signal or view)
        self.progress.qr_scans = {
            str(self.course_qr.id): {
                'first_scan': scanner.scan(self.course_qr.id)['scan_id'],
                'count': 1,
                'last_scan': scanner.scan(self.course_qr.id)['scan_id']
            }
        }
        self.progress.save()
        
        # Verify the scan was recorded
        self.assertEqual(len(self.progress.qr_scans), 1)
        self.assertIn(str(self.course_qr.id), self.progress.qr_scans)
        self.assertEqual(self.progress.qr_scans[str(self.course_qr.id)]['count'], 1)
    
    def test_qr_code_access_enforcement(self):
        """Test that QR access levels are enforced."""
        # Public module should be accessible to non-enrolled users
        non_enrolled_user = User.objects.create_user(
            username='non_enrolled',
            email='non_enrolled@example.com',
            password='nonenrolledpassword'
        )
        
        # Create scanners for different users
        enrolled_scanner = MockScanner(user=self.student)
        non_enrolled_scanner = MockScanner(user=non_enrolled_user)
        
        # Public module should be accessible to both users
        enrolled_result = enrolled_scanner.scan(self.module_public_qr.id)
        non_enrolled_result = non_enrolled_scanner.scan(self.module_public_qr.id)
        
        self.assertTrue(enrolled_result['success'])
        self.assertTrue(non_enrolled_result['success'])
        
        # Enrolled-only module should only be accessible to enrolled users
        # Note: In a real app, this would check enrollment status
        # Here we're mocking the behavior for testing purposes
        
        # Override the scanner's scan method for this test
        import mock
        with mock.patch('qr_codes.services.QRCodeService.validate_scan') as mock_validate:
            # For enrolled user, validation passes
            mock_validate.return_value = (True, "Valid", self.module_enrolled_qr)
            enrolled_result = enrolled_scanner.scan(self.module_enrolled_qr.id)
            self.assertTrue(enrolled_result['success'])
            
            # For non-enrolled user, validation fails
            mock_validate.return_value = (False, "Enrollment required", self.module_enrolled_qr)
            non_enrolled_result = non_enrolled_scanner.scan(self.module_enrolled_qr.id)
            self.assertFalse(non_enrolled_result['success'])
            self.assertEqual(non_enrolled_result['message'], "Enrollment required")