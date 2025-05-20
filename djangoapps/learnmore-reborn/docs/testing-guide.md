# Testing Guide for LearnMore Reborn

This guide explains how to write and run tests for the LearnMore Reborn application.

## Table of Contents

- [Test Structure](#test-structure)
- [Model Testing](#model-testing)
- [API Testing](#api-testing)
- [View Testing](#view-testing)
- [Running Tests](#running-tests)

## Test Structure

Tests in LearnMore Reborn are organized into the following structure:

```
app_name/
  tests/
    __init__.py
    test_models.py       # Tests for models
    test_views.py        # Tests for views
    test_api.py          # Tests for API endpoints
    test_forms.py        # Tests for forms
```

## Model Testing

Model tests focus on ensuring that the CRUD (Create, Read, Update, Delete) operations work correctly for each model.

### Example: Testing the Course Model

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class CourseModelTest(TestCase):
    """Tests for Course model CRUD operations."""
    
    def setUp(self):
        """Set up test data."""
        self.instructor = User.objects.create_user(
            username='instructor1',
            email='instructor1@example.com',
            password='testpass123'
        )
        
        self.course_data = {
            'title': 'Test Course',
            'description': 'Test course description',
            'instructor': self.instructor,
            'status': 'published',
            'enrollment_type': 'open',
        }
        
    def test_create_course(self):
        """Test creating a new course."""
        course = Course.objects.create(**self.course_data)
        
        # Assertions for creation
        self.assertIsNotNone(course.id)
        self.assertEqual(course.title, self.course_data['title'])
        # ... more assertions
    
    def test_read_course(self):
        """Test retrieving a course."""
        original = Course.objects.create(**self.course_data)
        
        # Retrieve by ID
        retrieved_by_id = Course.objects.get(id=original.id)
        self.assertEqual(retrieved_by_id.title, self.course_data['title'])
        # ... more assertions
    
    def test_update_course(self):
        """Test updating a course."""
        course = Course.objects.create(**self.course_data)
        
        # Update the course
        course.title = 'Updated Title'
        course.save()
        
        # Refresh from database
        course.refresh_from_db()
        self.assertEqual(course.title, 'Updated Title')
        # ... more assertions
    
    def test_delete_course(self):
        """Test deleting a course."""
        course = Course.objects.create(**self.course_data)
        course_id = course.id
        
        # Delete the course
        course.delete()
        
        # Verify deleted
        self.assertFalse(Course.objects.filter(id=course_id).exists())
```

### Guidelines for Model Testing

1. **Test All CRUD Operations**: Write separate tests for Create, Read, Update, and Delete operations
2. **Test Relationships**: Verify that related models are properly connected
3. **Test Constraints**: Check unique constraints, field validations, and other database constraints
4. **Test Model Methods**: Verify that custom methods and properties work correctly
5. **Test Edge Cases**: Test boundary conditions and error cases

## API Testing

API tests ensure that the REST API endpoints work as expected. LearnMore Reborn uses Django REST Framework's testing tools.

### Example: Testing Course API

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class CourseAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='pass'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course', 
            description='Test description',
            instructor=self.user
        )
        
        # Get authentication token
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'pass'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_list_courses(self):
        url = '/api/courses/courses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    # More API tests...
```

## View Testing

View tests verify that the Django views render correctly and process form submissions properly.

### Example: Testing View

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class CourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='pass'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test description',
            instructor=self.user
        )
        
    def test_course_list_view(self):
        # Login
        self.client.login(username='testuser', password='pass')
        
        # Access view
        url = reverse('course_list')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
        self.assertTemplateUsed(response, 'courses/course_list.html')
```

## Running Tests

### Running All Tests

```bash
python manage.py test
```

### Running App-Specific Tests

```bash
python manage.py test courses
```

### Running Specific Test Classes

```bash
python manage.py test courses.tests.test_models.CourseModelTest
```

### Running a Specific Test Method

```bash
python manage.py test courses.tests.test_models.CourseModelTest.test_create_course
```

## Best Practices

1. **Test Coverage**: Aim for high test coverage, especially for models and API endpoints
2. **Isolation**: Each test should be independent and not rely on other tests
3. **Fixtures**: Use Django fixtures or factory-boy for complex test data
4. **Mocking**: Use mocking for external services
5. **Documentation**: Document the purpose of test classes and methods
6. **Maintenance**: Update tests when the codebase changes

## Test Tags

Tests can be organized with tags that allow running specific groups of tests:

```python
from django.test import tag

@tag('models')
class CourseModelTest(TestCase):
    # Tests...

@tag('api')
class CourseAPITest(APITestCase):
    # Tests...
```

Run tests with a specific tag:

```bash
python manage.py test --tag=models
```

## Writing Testable Code

To make testing easier:

1. Follow the Single Responsibility Principle
2. Use dependency injection
3. Keep views thin and models fat
4. Avoid complex logic in templates
5. Use explicit model methods instead of implicit behavior