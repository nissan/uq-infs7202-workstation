# Testing Django Templates with REST Framework Integration

This guide explains approaches for testing Django templates when working with REST framework integration.

## Challenges of Template Testing with REST API Integration

When building a Django application that uses both traditional templates and a REST API, several testing challenges arise:

1. **Dual Data Sources**: Same data is often served through both templates and API endpoints
2. **Consistency Requirements**: Template views and API responses must remain consistent
3. **Authentication Verification**: Need to test that both interfaces respect the same permissions
4. **Response Format Differences**: Templates return HTML while APIs return JSON
5. **Integration Points**: Testing JavaScript code that consumes APIs and updates templates
6. **Request Processing Logic**: Testing common logic used for both template rendering and API responses

## Testing Approaches

### 1. Template-Specific Tests

Use Django's built-in `TestCase` class with `self.client.get()` to test templates directly:

```python
def test_course_detail_renders(self):
    """Test course detail page renders correctly"""
    # Get the response
    response = self.client.get(
        reverse('course-detail', kwargs={'slug': self.course.slug})
    )
    
    # Check status code
    self.assertEqual(response.status_code, 200)
    
    # Check template used
    self.assertTemplateUsed(response, 'courses/course-detail.html')
    
    # Check context
    self.assertEqual(response.context['course'], self.course)
    self.assertFalse(response.context['is_enrolled'])
```

### 2. API-Specific Tests

Use Django REST Framework's `APIClient` to test API endpoints:

```python
def test_course_detail_api(self):
    """Test course detail API endpoint"""
    # Login as regular user
    self.client.force_authenticate(user=self.user)
    
    # Create enrollment so user can see the course
    Enrollment.objects.create(
        user=self.user,
        course=self.course,
        status='active'
    )
    
    # Get the response
    url = reverse('course-detail', kwargs={'slug': self.course.slug})
    response = self.client.get(url)
    
    # Check status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Check response data
    self.assertEqual(response.data['title'], self.course.title)
    self.assertEqual(response.data['slug'], self.course.slug)
```

### 3. Integration Tests Between Templates and API

Test consistency between template context and API data:

```python
def test_api_and_template_consistency(self):
    """Test that API and template views return consistent data"""
    # Login for both API and template access
    self.client.login(username='testuser', password='testpassword')
    
    # Get API response
    api_url = reverse('course-detail', kwargs={'slug': self.course.slug})
    api_response = self.client.get(api_url, HTTP_ACCEPT='application/json')
    
    # Get template response
    template_url = reverse('course-detail', kwargs={'slug': self.course.slug})
    template_response = self.client.get(template_url, HTTP_ACCEPT='text/html')
    
    # Compare data
    self.assertEqual(api_response.status_code, status.HTTP_200_OK)
    self.assertEqual(template_response.status_code, status.HTTP_200_OK)
    
    # API should return JSON, template should return HTML
    self.assertIn('application/json', api_response['Content-Type'])
    self.assertIn('text/html', template_response['Content-Type'])
    
    # Template response should include context with course object
    self.assertIn('course', template_response.context)
    template_course = template_response.context['course']
    
    # Check core data consistency - API data vs template context data
    self.assertEqual(api_response.data['title'], template_course.title)
    self.assertEqual(api_response.data['slug'], template_course.slug)
    self.assertEqual(api_response.data['description'], template_course.description)
```

### 4. Testing Behavioral Flows

Test user flows that span both templates and API:

```python
def test_enrollment_status_reflected_in_both(self):
    """Test that enrollment status is consistently reflected in both template and API"""
    # Login
    self.client.login(username='testuser', password='testpassword')
    self.api_client.force_authenticate(user=self.user)
    
    # Get template responses for course
    template_url = reverse('course-detail', kwargs={'slug': self.course.slug})
    template_response = self.client.get(template_url)
    
    # Get API responses for enrollments
    api_url = reverse('enrolled-courses')
    api_response = self.api_client.get(api_url)
    
    # Template should show not enrolled initially
    self.assertFalse(template_response.context['is_enrolled'])
    
    # API should list no enrollments initially
    self.assertEqual(len(api_response.data), 0)
    
    # Now enroll in course
    self.client.get(reverse('course-enroll', kwargs={'slug': self.course.slug}))
    
    # Check template response for course again
    template_response = self.client.get(template_url)
    self.assertTrue(template_response.context['is_enrolled'])
    
    # Check API response again
    api_response = self.api_client.get(api_url)
    self.assertEqual(len(api_response.data), 1)
    self.assertEqual(api_response.data[0]['course'], self.course.id)
```

### 5. Testing Permission Consistency

Verify that permissions are enforced consistently:

```python
def test_permissions_consistency(self):
    """Test that permissions are enforced consistently in both templates and API"""
    # Create a course with restricted enrollment
    restricted_course = Course.objects.create(
        title='Restricted Course',
        slug='restricted-course',
        description='A restricted course',
        status='published',
        enrollment_type='restricted',
        instructor=self.instructor
    )
    
    # Try to access restricted course via template - should succeed for viewing
    template_url = reverse('course-detail', kwargs={'slug': restricted_course.slug})
    template_response = self.client.get(template_url)
    self.assertEqual(template_response.status_code, 200)
    
    # Try to enroll via template - should fail for restricted course
    enroll_url = reverse('course-enroll', kwargs={'slug': restricted_course.slug})
    template_enroll_response = self.client.get(enroll_url)
    
    # Should redirect with an error message
    self.assertEqual(template_enroll_response.status_code, 302)
    
    # Try to enroll via API - should also fail
    api_enroll_url = reverse('course-enroll', kwargs={'slug': restricted_course.slug})
    api_response = self.api_client.post(api_enroll_url)
    self.assertEqual(api_response.status_code, status.HTTP_400_BAD_REQUEST)
```

## Best Practices

1. **Separate Test Classes**: Organize tests into separate classes for templates, API, and integration tests
2. **Shared Test Setup**: Use common setup methods to ensure consistent test data
3. **Test Both Directions**: Test template-to-API and API-to-template interactions
4. **Mock External Services**: Use `unittest.mock` for external services used by both templates and APIs
5. **Test Content Negotiation**: Verify that the same URL returns appropriate format based on `Accept` header
6. **Test Error Handling**: Check that errors are presented appropriately in both templates and API responses
7. **Use TestCase Mixins**: Create mixins for common testing logic used across multiple test classes

## Example Test Organization

```
courses/
├── tests/
│   ├── __init__.py
│   ├── test_models.py                   # Model tests
│   ├── test_templates.py                # Template rendering tests
│   ├── test_api_views.py                # API endpoint tests
│   ├── test_template_api_integration.py # Integration tests
│   └── test_forms.py                    # Form tests
```

## Conclusion

Testing Django templates with REST framework integration requires a comprehensive approach that tests both interfaces separately and verifies their consistency. By using both `TestCase.client` and `APIClient`, you can ensure that your application behaves correctly regardless of how users interact with it.

This approach provides a solid foundation for maintaining a Django application that serves both template-based views and REST API endpoints while ensuring consistency between them.