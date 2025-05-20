# API Testing Guide for LearnMore Reborn

This guide outlines best practices for testing REST APIs in the LearnMore Reborn application using Django REST Framework's testing tools.

## Table of Contents

- [Test Structure](#test-structure)
- [Authentication Testing](#authentication-testing)
- [CRUD Operation Testing](#crud-operation-testing)
- [Authorization Testing](#authorization-testing)
- [Input Validation Testing](#input-validation-testing)
- [Edge Case Testing](#edge-case-testing)
- [Test Data Management](#test-data-management)
- [Best Practices](#best-practices)

## Test Structure

API tests in LearnMore Reborn are organized into the following structure:

```
app_name/
  api_tests.py          # Tests for API endpoints (viewsets)
  serializer_tests.py   # Tests for serializer validation
  tests/
    __init__.py         # Import all tests to ensure they're discovered
```

## Authentication Testing

Authentication is a critical component of API security. Test both successful and unsuccessful authentication scenarios.

### Example: Token Authentication Testing

```python
def test_user_login(self):
    """Test user login endpoint"""
    response = self.client.post(self.login_url, self.valid_login_data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn('access', response.data)
    self.assertIn('refresh', response.data)
    self.assertIn('user', response.data)

def test_user_login_invalid_credentials(self):
    """Test user login with invalid credentials"""
    invalid_data = self.valid_login_data.copy()
    invalid_data['password'] = 'wrongpass'
    response = self.client.post(self.login_url, invalid_data)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### Example: Token Refresh Testing

```python
def test_token_refresh(self):
    """Test refreshing the JWT token"""
    # First login to get tokens
    response = self.client.post(self.login_url, self.valid_login_data)
    refresh_token = response.data['refresh']
    
    # Refresh the access token
    response = self.client.post(self.token_refresh_url, {'refresh': refresh_token})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn('access', response.data)
```

## CRUD Operation Testing

Each API endpoint should be tested for Create, Read, Update, and Delete operations, as applicable.

### Example: Testing CRUD Operations

```python
def test_list_courses(self):
    """Test listing courses"""
    url = '/api/courses/courses/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data), 2)  # Assuming 2 courses exist

def test_retrieve_course(self):
    """Test retrieving a specific course"""
    url = f'/api/courses/courses/{self.course1.slug}/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['id'], self.course1.id)

def test_create_course(self):
    """Test creating a new course"""
    url = '/api/courses/courses/'
    data = {
        'title': 'New Course', 
        'description': 'New Desc', 
        'instructor': self.user.id,
        'status': 'published',
    }
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertTrue(Course.objects.filter(title='New Course').exists())

def test_update_course(self):
    """Test updating a course"""
    url = f'/api/courses/courses/{self.course1.slug}/'
    data = {
        'title': 'Updated Title',
        'description': self.course1.description,
        'instructor': self.user.id,
    }
    response = self.client.put(url, data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.course1.refresh_from_db()
    self.assertEqual(self.course1.title, 'Updated Title')

def test_delete_course(self):
    """Test deleting a course"""
    url = f'/api/courses/courses/{self.course1.slug}/'
    response = self.client.delete(url)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertFalse(Course.objects.filter(id=self.course1.id).exists())
```

## Authorization Testing

Authorization testing ensures that users can only access resources they are authorized to access. Test both positive and negative authorization scenarios.

### Example: Testing Role-Based Access Control

```python
def test_student_cannot_create_course(self):
    """Test that a regular student cannot create courses"""
    # Switch to student credentials
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
    
    url = '/api/courses/courses/'
    data = {
        'title': 'Student Course', 
        'description': 'Created by student', 
        'instructor': self.student_user.id,
    }
    
    response = self.client.post(url, data)
    
    # Student should not be allowed to create courses
    self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
    
    # Verify no course was created
    self.assertFalse(Course.objects.filter(title='Student Course').exists())
```

### Example: Testing Resource Ownership

```python
def test_student_cannot_see_other_student_progress(self):
    """Test student cannot see another student's progress"""
    # Switch to student credentials
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
    
    url = f'/api/progress/{self.other_student_progress.id}/'
    response = self.client.get(url)
    
    # Should not be able to access another student's progress
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
```

## Input Validation Testing

Input validation ensures that the API rejects invalid input. Test both valid and invalid inputs.

### Example: Serializer Validation Testing

```python
def test_valid_data(self):
    """Test that valid data passes validation."""
    serializer = CourseSerializer(data=self.valid_data)
    self.assertTrue(serializer.is_valid())

def test_missing_required_fields(self):
    """Test that missing required fields fail validation."""
    # Missing title
    invalid_data = self.valid_data.copy()
    invalid_data.pop('title')
    serializer = CourseSerializer(data=invalid_data)
    self.assertFalse(serializer.is_valid())
    self.assertIn('title', serializer.errors)
```

## Edge Case Testing

Edge case testing checks how the API handles boundary conditions and unexpected inputs.

### Example: Testing Enrollment Edge Cases

```python
def test_enroll_in_full_course(self):
    """Test enrolling in a course that has reached its capacity"""
    # Set up a course with max_students = 1
    self.course1.status = 'published'
    self.course1.max_students = 1
    self.course1.save()
    
    # Create another user and enroll them first to fill the course
    other_user = User.objects.create_user(username='otheruser', password='pass')
    Enrollment.objects.create(user=other_user, course=self.course1, status='active')
    
    # Try to enroll our test user
    url = f'/api/courses/courses/{self.course1.slug}/enroll/'
    response = self.client.post(url)
    
    # Should not be allowed to enroll in a full course
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn('error', response.data)
```

## Test Data Management

Proper test data management is essential for effective API testing.

### Best Practices for Test Data:

1. **Use setUp method**: Create necessary test data in the setUp method
2. **Create minimal data**: Only create the data necessary for the test
3. **Use descriptive names**: Use descriptive names for test data to make tests readable
4. **Isolation**: Ensure each test is isolated and does not depend on other tests

### Example: setUp Method

```python
def setUp(self):
    # Create instructor user
    self.instructor = User.objects.create_user(username='instructor', password='pass')
    self.instructor.profile.is_instructor = True
    self.instructor.profile.save()
    
    # Create student user
    self.student = User.objects.create_user(username='student', password='pass')
    self.student.profile.is_instructor = False
    self.student.profile.save()
    
    # Create test courses
    self.course1 = Course.objects.create(
        title='Course 1', 
        description='Desc 1', 
        instructor=self.instructor,
        status='published'
    )
    
    # Login and get tokens
    response = self.client.post('/api/users/login/', {
        'username': 'instructor',
        'password': 'pass'
    })
    self.instructor_token = response.data['access']
    
    # Default to instructor credentials
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.instructor_token}')
```

## Best Practices

1. **Test for Success and Failure**: Test both successful and unsuccessful scenarios
2. **Test for Authentication and Authorization**: Ensure users can only access resources they should
3. **Test for Input Validation**: Ensure the API properly validates input
4. **Test for Error Handling**: Ensure the API returns appropriate error messages
5. **Test for CRUD Operations**: Test Create, Read, Update, and Delete operations
6. **Test for Edge Cases**: Test boundary conditions and unexpected inputs
7. **Test for Performance**: Check that the API performs within acceptable limits
8. **Document Tests**: Use descriptive test names and docstrings
9. **Organize Tests**: Group related tests together
10. **Use Fixtures**: Use fixture data for more complex scenarios

### Example: Well-Documented Test

```python
def test_list_modules_as_student(self):
    """
    Test that a student can only see modules from enrolled courses.
    
    This test verifies that:
    1. Students can access modules for courses they're enrolled in
    2. Students cannot access modules for courses they're not enrolled in
    3. The correct number of modules is returned
    """
    # Switch to student credentials
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_token}')
    
    url = '/api/courses/modules/'
    response = self.client.get(url)
    
    # Assertions
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data), 1)  # Should only see module1
    self.assertEqual(response.data[0]['id'], self.module1.id)
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test courses
python manage.py test users
python manage.py test progress

# Run a specific test module or class
python manage.py test courses.api_tests
python manage.py test courses.serializer_tests
python manage.py test courses.module_quiz_tests

# Run a specific test method
python manage.py test courses.api_tests.CourseAPITest.test_list_courses
```