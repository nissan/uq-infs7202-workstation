"""
Main test file that imports all model tests to ensure they run together.
"""

from .test_category_model import TestCategoryModel
from .test_course_model import TestCourseModel
from .test_module_model import TestModuleModel
from .test_content_model import TestContentModel
from .test_enrollment_model import TestCourseEnrollmentModel
from .test_module_progress_model import TestModuleProgressModel
from .test_quiz_model import TestQuizModel
from .test_question_model import TestQuestionModel
from .test_quiz_attempt_model import TestQuizAttemptModel

# This file serves as an entry point for running all model tests
# The tests themselves are defined in the imported modules