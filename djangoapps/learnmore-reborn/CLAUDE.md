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
     - Currently on Phase 5 (Quiz System - Basics)

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
   - Tests are organized into categories using pytest markers: api, template, integration

4. **Authentication System**:
   - JWT-based authentication using Simple JWT
   - Custom user profiles with instructor permissions
   - Google OAuth integration (configured in settings)

## Migration Plan

The project follows a phased approach to rebuild the LMS:

1. Phase 1: Core data & CRUD
2. Phase 2: User auth & profiles
3. Phase 3: Course catalog & enrollment
4. Phase 4: Learning interface & progress tracking 
5. Phase 5: Quiz system – basics (Current Focus)
6. Phase 6-12: Additional features (advanced quizzes, admin dashboards, AI tutor, etc.)

For each phase, development follows a consistent slice-based approach:
1. Models → serializers → views → URLs → templates → tests
2. Documentation updates
3. Test execution and validation
4. Feature branch and pull request workflow

## Important Notes

- When adding quiz functionality, refer to `PHASE_5_CHECKLIST.md` for the full requirements
- Use the pytest testing framework over Django's TestCase for more reliable test results
- JWT authentication is used in production but bypassed in tests
- The current git branch is `feature/phase5-quiz-system`