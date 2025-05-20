# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Django-based Learning Management System (LMS) projects, with two main versions:

1. **LearnMore Reborn** (`djangoapps/learnmore-reborn/`):
   - Django 4.x with REST Framework integration
   - JWT authentication
   - Basic apps: courses, progress, users, ai_tutor, analytics

2. **LearnMore Plus** (`djangoapps/learnmore_plus/`):
   - More feature-rich version with additional functionality
   - Advanced modular architecture with separate apps for each feature
   - Includes AI Tutor with LangChain and Ollama integration
   - Uses Tailwind CSS for UI components

## Setup and Installation

### LearnMore Reborn

```bash
# Navigate to the project
cd djangoapps/learnmore-reborn/

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (.env file)
# Create .env file with:
# DEBUG=True
# SECRET_KEY=your-secret-key
# ALLOWED_HOSTS=127.0.0.1,localhost

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### LearnMore Plus

```bash
# Navigate to the project
cd djangoapps/learnmore_plus/

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies (for development)
pip install -r requirements/dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Reset and seed database with demo data
python manage.py reset_db

# Run development server
python manage.py runserver
```

## Development and Testing Commands

### LearnMore Plus Commands

```bash
# Run the development server
python manage.py runserver

# Run all tests
pytest
# or
./run_tests.sh

# Run tests for a specific app
pytest apps/core/
# or
./run_tests.sh core

# Run a specific test
pytest apps/core/tests.py::TestClass::test_method
# or
./run_tests.sh core TestClass.test_method

# Run test categories
pytest -m unit       # Run unit tests
pytest -m integration # Run integration tests
pytest -m ui         # Run UI component tests
pytest -m slow       # Run slow tests
pytest -m "not slow" # Skip slow tests

# Check test coverage
coverage run -m pytest && coverage report

# Template syntax checking
python check_templates.py

# Playwright E2E tests
cd tests/e2e
npm install (first time only)
npx playwright install (first time only)
npx playwright test
npx playwright test --debug
```

### Common Management Commands

```bash
# Create migrations
python manage.py makemigrations [app_name]

# Apply migrations
python manage.py migrate [app_name]

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Shell plus (for debugging)
python manage.py shell_plus

# Reset and seed database with demo data
python manage.py reset_db

# Seed AI tutor demo data
python manage.py seed_ai_tutor_demo

# Index course content for AI tutor
python manage.py index_course_content
```

## Architecture

### LearnMore Plus Architecture

The LearnMore Plus project is organized using a Django app-based architecture:

1. **Apps Layer**:
   - `accounts`: User management, authentication, and profiles
   - `ai_tutor`: AI-powered tutoring with LangChain and Ollama integration
   - `core`: Core app with base functionality, shared components, and utilities
   - `courses`: Course management, modules, content, and quiz system
   - `dashboard`: Admin dashboard and analytics
   - `qr_codes`: QR code generation for courses and modules
   - `theme`: Theming and Tailwind CSS support

2. **Project Settings**:
   - Uses split settings for different environments:
     - `base.py`: Common settings
     - `dev.py`: Development settings 
     - `prod.py`: Production settings
     - `test.py`: Test settings

3. **Templates Structure**:
   - Root templates for base layouts
   - Component-based UI architecture
   - App-specific templates in each app's templates directory

4. **Static Files**:
   - CSS: Tailwind CSS for styling
   - JS: JavaScript files for interactive functionality
   - Images: SVG and image resources

5. **Test Architecture**:
   - Django test framework with pytest
   - Playwright for end-to-end browser testing
   - Visual regression testing
   - Accessibility testing

## Important Design Patterns

1. **Template Component System**:
   - Uses an atomic design-inspired component structure
   - Components are modular and reusable

2. **User Role-Based Access**:
   - Uses Django's group-based permissions
   - Main roles: Admin, Course Coordinator, Instructor, Student
   - Context processors add role information to templates

3. **AI Tutor System**:
   - Uses LangChain for AI integration
   - Supports multiple backends (Ollama, OpenAI)
   - Uses RAG (Retrieval Augmented Generation) for context-aware responses

4. **Quiz System**:
   - Multiple question types
   - Time-tracking for detailed analytics
   - Auto-submission for timed quizzes

## Database Models

Main models in the LearnMore Plus system:

- **Accounts**: `User`, `UserProfile`, `UserPreferences`
- **Courses**: `Course`, `Module`, `Content`, `Enrollment`
- **Quiz**: `Quiz`, `Question`, `Answer`, `QuizAttempt`, `QuestionAttempt`
- **AI Tutor**: `TutorSession`, `TutorMessage`, `TutorContext`
- **QR Codes**: `QRCode`, `QRCodeScan`, `QRCodeStatistics`

## Deployment

The project is configured for deployment on Railway.app with:

- Configuration-as-code via `railway.toml`
- Production settings in `settings/prod.py`
- WhiteNoise for static file serving
- Procfile for defining Railway processes
- Support for PostgreSQL database in production