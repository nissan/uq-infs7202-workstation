# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Django-based Learning Management System (LMS) projects, with two main versions:

1. **LearnMore Reborn** (`djangoapps/learnmore-reborn/`):
   - Django 4.x with REST Framework integration
   - JWT authentication
   - Basic apps: courses, progress, users, ai_tutor, analytics
   - Current Development Focus: Migrating and rebuilding the LMS
     - Following phased migration plan in `MIGRATION-PLAN.md`
     - Currently on Phase 6 (Quiz System - Advanced Features)

## Common Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver
```

### Testing Commands

#### Running Tests with pytest (Preferred)
```bash
# Run all tests with the provided script
./run_pytest.sh

# Run only template tests
./run_pytest.sh -m template

# Run only API tests
./run_pytest.sh -m api

# Run only integration tests
./run_pytest.sh -m integration

# Run unit tests
./run_pytest.sh -m unit

# Run with coverage report
./run_pytest.sh -c
```

#### Running Tests Directly with pytest
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest courses/tests/test_pytest.py

# Run tests matching a specific name pattern
python -m pytest -k "catalog"

# Run multiple test categories
python -m pytest -m "template or api"
```

#### Running Django Tests (Note: Some tests are expected to fail)
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test courses
python manage.py test users
python manage.py test progress

# Run a specific test module or class
python manage.py test courses.api_tests
python manage.py test courses.tests.test_models
python manage.py test courses.api_tests.CourseAPITest
```

### Running Specific Quiz Tests

```bash
# Run quiz model tests
python -m pytest courses/tests/test_quiz_model.py

# Run quiz API tests
python -m pytest courses/tests/test_quiz_api.py

# Run quiz integration tests
python -m pytest courses/tests/test_quiz_integration.py

# Run time limit tests
python -m pytest courses/tests/test_quiz_time_limits.py

# Run randomization tests
python -m pytest courses/tests/test_quiz_randomization.py

# Run attempt limit tests
python -m pytest courses/tests/test_quiz_attempt_limits.py

# Run essay question tests
python -m pytest courses/tests/test_essay_questions.py
python -m pytest courses/tests/test_essay_questions_advanced.py
python -m pytest courses/tests/test_essay_questions_integration.py

# Run enhanced feedback tests
python -m pytest courses/tests/test_enhanced_feedback.py

# Run media support tests
python -m pytest courses/tests/test_media_support.py

# Run prerequisite surveys tests
python -m pytest courses/tests/test_prerequisite_surveys.py
```

## Code Architecture

The project follows a typical Django architecture with apps for different functionality areas:

1. **Core Django Configuration** (`learnmore/`):
   - `settings.py`: Main settings file with JWT authentication configuration
   - `test_settings.py`: Special settings for pytest that bypass authentication
   - `urls.py`: Main URL routing

2. **Apps Structure**:
   - **courses**: Core course management, modules, quizzes
   - **progress**: Learning progress tracking
   - **users**: User authentication, profiles, permissions
   - **analytics**: Usage analytics and reporting
   - **ai_tutor**: AI-based tutoring system (planned)

3. **Testing Approach**:
   - Two parallel test systems: Django TestCase and pytest
   - pytest is preferred as it uses special test settings with authentication bypass
   - Tests are organized into categories using pytest markers: api, template, integration, unit, slow
   - To run tests successfully, use pytest with the provided run_pytest.sh script or directly with python -m pytest

4. **Authentication System**:
   - JWT-based authentication using Simple JWT
   - Custom user profiles with instructor permissions
   - Google OAuth integration (configured in settings)

5. **Quiz System Architecture**:
   - Abstract `Question` model with subclasses for different question types
   - `Quiz` model associated with course modules
   - `QuizAttempt` tracks user attempts at quizzes
   - `QuestionResponse` stores user answers to individual questions
   - Integration with progress tracking via module completion

## Migration Plan

The project follows a phased approach to rebuild the LMS:

1. Phase 1: Core data & CRUD (Completed)
2. Phase 2: User auth & profiles (Completed)
3. Phase 3: Course catalog & enrollment (Completed)
4. Phase 4: Learning interface & progress tracking (Completed)
5. Phase 5: Quiz system – basics (Completed)
6. Phase 6: Quiz system – advanced (Current Focus)
7. Phase 7-12: Additional features (admin dashboards, AI tutor, etc.)

For each phase, development follows a consistent slice-based approach:
1. Models → serializers → views → URLs → templates → tests
2. Documentation updates
3. Test execution and validation
4. Feature branch and pull request workflow

## Phase 6: Advanced Quiz System

Phase 6 extends the basic quiz system with these key features:

1. **Essay Questions**: 
   - Text-based responses with manual grading
   - Rubrics and instructor feedback
   - Separate workflow for instructor review

2. **Media Support**: 
   - Image support in questions and choices
   - External media URL integration
   - Responsive media display

3. **Advanced Time Limits**:
   - Server-side time validation
   - Grace periods and extensions
   - Per-question time tracking

4. **Prerequisite Surveys**:
   - Survey dependency system
   - Conditional content access
   - Prerequisite enforcement

5. **Enhanced Feedback**:
   - Multi-level feedback mechanisms
   - Instructor annotations
   - Delayed feedback options

6. **Advanced Scoring**:
   - Partial credit for multiple-choice
   - Custom scoring rubrics
   - Question weighting

7. **Analytics Enhancements**:
   - Instructor analytics dashboards
   - Question performance metrics
   - Student performance insights

8. **Security & UI Improvements**:
   - Enhanced quiz access controls
   - Improved randomization options
   - Mobile responsive interface
   - Accessibility improvements

## Testing Notes

### Important Testing Tips
- Always run tests using pytest (`python -m pytest` or `./run_pytest.sh`) rather than Django's test runner
- The pytest configuration uses `learnmore.test_settings.py` which bypasses authentication restrictions
- Tests are categorized with markers (api, template, integration, unit) to allow selective testing
- The custom test settings allow tests to pass despite authentication requirements in the code
- When modifying or adding quiz functionality, ensure you add corresponding tests under the appropriate marker

### Understanding Test Failures
If you encounter test failures related to authentication (401 Unauthorized), you might be:
1. Using Django's test runner instead of pytest
2. Not using the correct pytest configuration from pytest.ini
3. Missing authentication bypass in the test case

## Important Notes

- When adding quiz functionality, refer to `PHASE_6_CHECKLIST.md` for the full requirements
- Use the pytest testing framework over Django's TestCase for more reliable test results
- JWT authentication is used in production but bypassed in tests
- The current git branch is `feature/phase6-quiz-advanced`
- Refer to `QUIZ_SYSTEM.md` for comprehensive documentation of the quiz system architecture
- When implementing new features, always add corresponding tests under the appropriate marker category
- Check `PHASE_6_PROGRESS.md` to understand the current implementation status of Phase 6 features