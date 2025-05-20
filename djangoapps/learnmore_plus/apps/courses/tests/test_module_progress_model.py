import pytest
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Category, CourseEnrollment, ModuleProgress

User = get_user_model()

@pytest.mark.django_db
class TestModuleProgressModel:
    """
    Tests for the ModuleProgress model CRUD operations.
    """
    
    @pytest.fixture
    def setup_data(self):
        """Set up test data for module progress testing."""
        # Create a category
        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="Test category description"
        )
        
        # Create a coordinator
        coordinator = User.objects.create_user(
            username='test_coordinator',
            email='coordinator@test.com',
            password='password123'
        )
        
        # Create a course
        course = Course.objects.create(
            title="Test Course for Module Progress",
            slug="test-course-for-module-progress",
            description="Test course for module progress testing",
            category=category,
            coordinator=coordinator,
            status='published'
        )
        
        # Create a module
        module = Module.objects.create(
            course=course,
            title="Test Module for Progress",
            description="Test module for progress testing",
            order=1
        )
        
        # Create a student
        student = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='password123'
        )
        
        # Create an enrollment
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            status='active',
            progress=0
        )
        
        return {
            'course': course, 
            'module': module, 
            'student': student, 
            'enrollment': enrollment
        }
    
    def test_create_module_progress(self, setup_data):
        """Test creating new module progress."""
        data = setup_data
        enrollment = data['enrollment']
        module = data['module']
        
        # Create the module progress
        module_progress = ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status='not_started',
            progress=0
        )
        
        # Assertions for creation
        assert module_progress.id is not None
        assert module_progress.enrollment == enrollment
        assert module_progress.module == module
        assert module_progress.status == 'not_started'
        assert module_progress.progress == 0
        assert module_progress.started_at is None
        assert module_progress.completed_at is None
    
    def test_read_module_progress(self, setup_data):
        """Test retrieving module progress."""
        data = setup_data
        enrollment = data['enrollment']
        module = data['module']
        
        # Create module progress
        module_progress = ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status='not_started',
            progress=0
        )
        
        # Retrieve by ID
        retrieved_by_id = ModuleProgress.objects.get(id=module_progress.id)
        assert retrieved_by_id.enrollment == enrollment
        assert retrieved_by_id.module == module
        
        # Retrieve by enrollment and module
        retrieved_by_enrollment_module = ModuleProgress.objects.get(
            enrollment=enrollment, 
            module=module
        )
        assert retrieved_by_enrollment_module.id == module_progress.id
        
        # Test filtering
        enrollment_progress = ModuleProgress.objects.filter(enrollment=enrollment)
        assert module_progress in enrollment_progress
        
        not_started_progress = ModuleProgress.objects.filter(status='not_started')
        assert module_progress in not_started_progress
    
    def test_update_module_progress(self, setup_data):
        """Test updating module progress."""
        data = setup_data
        enrollment = data['enrollment']
        module = data['module']
        
        # Create module progress
        module_progress = ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status='not_started',
            progress=0
        )
        
        # Update to in progress
        now = timezone.now()
        module_progress.status = 'in_progress'
        module_progress.progress = 50
        module_progress.started_at = now
        module_progress.save()
        
        # Refresh from database
        module_progress.refresh_from_db()
        
        # Assertions for in progress
        assert module_progress.status == 'in_progress'
        assert module_progress.progress == 50
        assert module_progress.started_at is not None
        assert module_progress.completed_at is None
        
        # Update to completed
        module_progress.status = 'completed'
        module_progress.progress = 100
        module_progress.completed_at = timezone.now()
        module_progress.save()
        
        # Refresh from database
        module_progress.refresh_from_db()
        
        # Assertions for completed
        assert module_progress.status == 'completed'
        assert module_progress.progress == 100
        assert module_progress.started_at is not None
        assert module_progress.completed_at is not None
    
    def test_delete_module_progress(self, setup_data):
        """Test deleting module progress."""
        data = setup_data
        enrollment = data['enrollment']
        module = data['module']
        
        # Create module progress
        module_progress = ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status='not_started',
            progress=0
        )
        
        # Verify created
        progress_id = module_progress.id
        assert ModuleProgress.objects.filter(id=progress_id).exists()
        
        # Delete the module progress
        module_progress.delete()
        
        # Verify deleted
        assert not ModuleProgress.objects.filter(id=progress_id).exists()
    
    def test_unique_constraint(self, setup_data):
        """Test the unique constraint of enrollment and module."""
        data = setup_data
        enrollment = data['enrollment']
        module = data['module']
        
        # Create module progress
        ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status='not_started',
            progress=0
        )
        
        # Attempt to create another progress for the same enrollment and module
        # This should raise an IntegrityError due to the unique_together constraint
        with pytest.raises(Exception) as excinfo:
            ModuleProgress.objects.create(
                enrollment=enrollment,
                module=module,
                status='in_progress',
                progress=50
            )
    
    def test_str_representation(self, setup_data):
        """Test the string representation of module progress."""
        data = setup_data
        enrollment = data['enrollment']
        module = data['module']
        
        module_progress = ModuleProgress.objects.create(
            enrollment=enrollment,
            module=module,
            status='not_started',
            progress=0
        )
        
        expected_str = f"{enrollment} - {module.title}"
        assert str(module_progress) == expected_str