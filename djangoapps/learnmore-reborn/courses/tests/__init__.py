# courses tests package
# Import the API tests to ensure they are discovered
from courses.api_tests import CourseSerializerTest, CourseAPITest
from courses.module_quiz_tests import ModuleQuizAPITest
from courses.serializer_tests import (
    CourseSerializerValidationTest,
    ModuleSerializerValidationTest,
    QuizSerializerValidationTest,
    EnrollmentSerializerValidationTest
)
from courses.template_tests import TemplateViewTests
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase