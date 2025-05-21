"""
Configuration for pytest.
"""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from courses.models import Course, Module, Quiz, Enrollment
from progress.models import Progress
from qr_codes.models import QRCode, QRCodeScan, QRCodeBatch
from qr_codes.tests.utils import MockQRGenerator, create_test_qr_code, create_test_batch

User = get_user_model()

@pytest.fixture
def instructor_user():
    """Create a test instructor user."""
    return User.objects.create_user(
        username='instructor',
        email='instructor@example.com',
        password='instructorpassword',
        is_staff=True
    )


@pytest.fixture
def student_user():
    """Create a test student user."""
    return User.objects.create_user(
        username='student',
        email='student@example.com',
        password='studentpassword'
    )


@pytest.fixture
def test_course(instructor_user):
    """Create a test course."""
    return Course.objects.create(
        title='Test Course',
        description='A test course',
        instructor=instructor_user
    )


@pytest.fixture
def test_module(test_course):
    """Create a test module."""
    return Module.objects.create(
        title='Test Module',
        description='A test module',
        course=test_course,
        order=1
    )


@pytest.fixture
def test_quiz(test_module):
    """Create a test quiz."""
    return Quiz.objects.create(
        title='Test Quiz',
        description='A test quiz',
        module=test_module,
        time_limit=30
    )


@pytest.fixture
def test_enrollment(student_user, test_course):
    """Create a test enrollment."""
    return Enrollment.objects.create(
        user=student_user,
        course=test_course,
        status='active'
    )


@pytest.fixture
def test_progress(student_user, test_course):
    """Create a test progress."""
    return Progress.objects.create(
        user=student_user,
        course=test_course,
        status='in_progress'
    )


@pytest.fixture
def course_qr_code(test_course):
    """Create a QR code for a course."""
    return create_test_qr_code(test_course)


@pytest.fixture
def module_qr_code(test_module):
    """Create a QR code for a module."""
    return create_test_qr_code(test_module, access_level='enrolled')


@pytest.fixture
def quiz_qr_code(test_quiz):
    """Create a QR code for a quiz."""
    return create_test_qr_code(test_quiz, access_level='enrolled', max_scans=5)


@pytest.fixture
def qr_batch(instructor_user, test_course):
    """Create a QR code batch."""
    batch = create_test_batch(
        name='Test Batch',
        content_type_model='courses.course',
        user=instructor_user
    )
    
    # Create QR codes in the batch
    content_type = ContentType.objects.get_for_model(Course)
    qr_code = QRCode.objects.create(
        content_type=content_type,
        object_id=test_course.id,
        is_active=True,
        access_level='public',
        batch=batch
    )
    
    # Generate mock image
    MockQRGenerator.generate_qr_image(qr_code)
    
    # Update batch count
    batch.codes_count = 1
    batch.save()
    
    return batch