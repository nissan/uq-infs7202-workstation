import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.courses.models import Course, Module, Content


User = get_user_model()


@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123'
    )


@pytest.fixture
def instructor_user():
    """Create and return an instructor user."""
    user = User.objects.create_user(
        username='instructor',
        email='instructor@example.com',
        password='instructorpassword123'
    )
    group, _ = Group.objects.get_or_create(name='Instructor')
    user.groups.add(group)
    return user


@pytest.fixture
def coordinator_user():
    """Create and return a coordinator user."""
    user = User.objects.create_user(
        username='coordinator',
        email='coordinator@example.com',
        password='coordinatorpassword123'
    )
    group, _ = Group.objects.get_or_create(name='Course Coordinator')
    user.groups.add(group)
    return user


@pytest.fixture
def student_user():
    """Create and return a student user."""
    return User.objects.create_user(
        username='student',
        email='student@example.com',
        password='studentpassword123'
    )


@pytest.fixture
def sample_course(instructor_user):
    """Create and return a sample course."""
    return Course.objects.create(
        title='Test Course',
        slug='test-course',
        description='A test course',
        coordinator=instructor_user,
        status='published'
    )


@pytest.fixture
def sample_module(sample_course):
    """Create and return a sample module."""
    return Module.objects.create(
        course=sample_course,
        title='Test Module',
        description='A test module',
        order=1
    )


@pytest.fixture
def sample_content(sample_module):
    """Create and return a sample content item."""
    return Content.objects.create(
        module=sample_module,
        title='Test Content',
        content_type='text',
        content='Test content text',
        order=1
    )