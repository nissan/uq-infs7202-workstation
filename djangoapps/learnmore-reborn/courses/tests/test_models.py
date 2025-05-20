"""
Test runner for all model tests.
This file imports all the model test classes to ensure they run together.
"""

from .test_course_model import CourseModelTest
from .test_module_model import ModuleModelTest
from .test_quiz_model import QuizModelTest
from .test_enrollment_model import EnrollmentModelTest

# Importing all test classes ensures they run when you run:
# python manage.py test courses.tests.test_models