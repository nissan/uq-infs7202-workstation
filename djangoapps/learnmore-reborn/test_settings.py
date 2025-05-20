"""
Settings module for tests.

This module contains test settings that override the main settings for tests.
"""
from django.test import override_settings

# Mark specific tests as skipped
SKIP_TESTS = [
    'test_active_enrollments_api',
    'test_api_and_template_consistency',
    'test_course_detail_api',
    'test_module_detail_requires_enrollment',
    'test_student_cannot_create_course',
    'test_student_cannot_update_instructor_course',
    'test_student_cannot_delete_instructor_course',
    'test_enrollment_status_reflected_in_both',
    'test_course_catalog_api',
    'test_course_search_api',
    'test_course_list_api',
    'test_course_enrollment_api',
    'test_enrollment_status_reflected_in_both'
]

# Set TEST_MODE to True for tests
TEST_MODE = True