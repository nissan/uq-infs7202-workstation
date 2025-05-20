# LearnMore Reborn - Django SaaS Learning Platform


This is the initial scaffold for the Enhanced LearnMore project, a Django-based SaaS learning platform with Django REST Framework (DRF) integration, `.env` configuration, and admin setup.

### ✅ Features Configured
- Django 4.x
- Django REST Framework
- django-environ for `.env` config
- django-cors-headers
- Virtual environment
- Basic app structure: `courses`, `progress`, `users`
- Initial `Course` and `Progress` models
- Admin user created
- Comprehensive test suite
- `requirements.txt` frozen

---

## 📝 Setup Instructions

1. **Clone the repo & activate virtual environment:**

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
```

## Phase 1 Migration Checklist

Track the core data & CRUD migration tasks in [PHASE_1_CHECKLIST.md](PHASE_1_CHECKLIST.md).

Install dependencies:

```bash
pip install -r requirements.txt
```

Create .env file at project root:
```ini
DEBUG=True
SECRET_KEY=django-insecure-replace-this-with-a-better-key
ALLOWED_HOSTS=127.0.0.1,localhost
```

```bash
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run development server:

```bash
python manage.py runserver
Visit: http://127.0.0.1:8000/admin/

## 🧪 Test Suite

The application includes comprehensive tests for models, serializers, and API endpoints:

### Testing Framework
- Django's built-in `TestCase` for model and serializer tests
- `APITestCase` from Django REST Framework for API endpoint testing
- Comprehensive API authentication tests using JWT tokens

### Running Tests
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

#### Custom Test Runner

The application uses a custom test runner (`QuietTestRunner`) to suppress expected warnings during tests. This runner temporarily adjusts the logging level during test execution to hide warnings that are expected as part of testing API validation:

- 400 Bad Request responses (when testing validation)
- 401 Unauthorized responses (when testing authentication)
- Other expected error responses that are part of test cases

This makes the test output cleaner while still ensuring proper test coverage of error cases.

### Test Structure
The test suite is organized into different categories:

1. **API Tests**: Tests for API endpoints and serializers
   - `api_tests.py` in each app
   - Test API endpoints, request/response handling, and authentication

2. **Model Tests**: Tests for models and database operations
   - Located in `tests/` directory in each app
   - Test model validation, fields, and methods

### Test Coverage
- **User Tests**: Authentication (register, login, logout), profile management, Google OAuth
- **Course Tests**: Course CRUD operations, catalog listing, searching, enrollment
- **Progress Tests**: Progress tracking, serialization, and updates
- **Serializer Tests**: Validation of serializer fields and behavior

## 🔐 Authentication & Profile Management

The application uses Django's built-in User model with a custom UserProfile extension for additional user information. Authentication is handled through JWT tokens.

## 📚 Course Catalog & Enrollment

The platform features a comprehensive course catalog with enrollment management capabilities. Users can browse courses, filter by enrollment type, search for specific courses, and enroll in courses of interest.

## 📊 Learning Progress Tracking

The platform includes a robust progress tracking system that allows users to track their learning journey through courses. Key features include:

- **Course Progress**: Track overall completion percentage for each course
- **Module-Level Progress**: Track completion status of individual modules
- **Time Tracking**: Automatically track time spent on learning activities
- **Prerequisites**: Module prerequisites enforcement ensures proper learning sequence
- **Learning Statistics**: View comprehensive learning statistics across all courses
- **Continue Learning**: Easily pick up where you left off in your learning journey
- **Progress Reset**: Reset progress for a course to start over

For detailed information on the progress tracking implementation, see [docs/PROGRESS_TRACKING.md](docs/PROGRESS_TRACKING.md).

## 📝 Quiz System

The platform features a comprehensive quiz system integrated with courses and progress tracking:

- **Multiple Quiz Types**: Support for both graded quizzes and ungraded surveys
- **Question Formats**: Multiple-choice and True/False questions with individual feedback
- **Time Limits**: Optional time limits for quiz completion
- **Multiple Attempts**: Configure how many times learners can take a quiz
- **Randomization**: Option to randomize question order for each attempt
- **Detailed Analytics**: Track scores, time spent, and passing rates
- **Progress Integration**: Quizzes are integrated with the progress tracking system
- **Instructor Controls**: Instructors can create, edit, and manage quizzes for their courses

Key features include:
- Dynamic scoring and feedback for each question
- Automatic pass/fail evaluation based on configurable passing scores
- Time tracking for each question and overall quiz attempts
- Support for multiple correct answers in multiple-choice questions

### Available Endpoints

- `POST /api/users/register/` - Register a new user
- `POST /api/users/login/` - Login and get JWT tokens
- `POST /api/users/logout/` - Logout and invalidate refresh token
- `POST /api/users/token/refresh/` - Get new access token
- `GET/PUT /api/users/profile/` - Get/Update user profile
- `POST /api/users/google-auth/` - Google OAuth authentication

For detailed API documentation, see [users/API_DOCUMENTATION.md](users/API_DOCUMENTATION.md).

### Course Catalog & Enrollment Endpoints

- `GET /api/courses/catalog/` - List all published courses
- `GET /api/courses/catalog/search/` - Search for courses by title or description
- `POST /api/courses/{slug}/enroll/` - Enroll in a course
- `POST /api/courses/{slug}/unenroll/` - Unenroll from a course
- `GET /api/courses/enrolled/` - List enrolled courses

For detailed API documentation on course catalog and enrollment, see [courses/API_DOCUMENTATION.md](courses/API_DOCUMENTATION.md).

### Progress Tracking Endpoints

- `GET /api/progress/progress/` - List all progress records for the current user
- `GET /api/progress/progress/{id}/` - Get details for a specific progress record
- `GET /api/progress/progress/course/?course_id={id}` - Get progress for a specific course
- `GET /api/progress/progress/continue_learning/` - Get the next incomplete module to continue learning
- `GET /api/progress/progress/stats/` - Get learning statistics across all courses
- `POST /api/progress/progress/{id}/reset/` - Reset progress for a specific course
- `GET /api/progress/module-progress/` - List all module progress records for the current user
- `POST /api/progress/module-progress/{id}/complete/` - Mark a module as completed
- `POST /api/progress/module-progress/{id}/update_position/` - Update content position (for video/audio)
- `POST /api/progress/module-progress/{id}/add_time/` - Add time spent on a module

### Quiz System Endpoints

- `GET /api/quizzes/` - List all quizzes available to the user
- `GET /api/quizzes/{id}/` - Get details for a specific quiz
- `POST /api/quizzes/{id}/start-attempt/` - Start a new quiz attempt
- `GET /api/quizzes/{id}/attempts/` - List all attempts for a specific quiz
- `GET /api/quiz-attempts/` - List all quiz attempts for the current user
- `GET /api/quiz-attempts/{id}/` - Get details for a specific quiz attempt
- `POST /api/quiz-attempts/{id}/submit-response/` - Submit an answer to a question
- `POST /api/quiz-attempts/{id}/complete/` - Mark a quiz attempt as completed
- `POST /api/quiz-attempts/{id}/timeout/` - Mark a quiz attempt as timed out
- `POST /api/quiz-attempts/{id}/abandon/` - Mark a quiz attempt as abandoned
- `GET /api/quiz-attempts/{id}/result/` - Get results for a completed quiz attempt
- `GET /api/multiple-choice-questions/` - List multiple-choice questions (instructors only)
- `GET /api/true-false-questions/` - List true/false questions (instructors only)

### User Profile Fields

- `bio` - User biography (optional)
- `student_id` - Student ID number (optional)
- `department` - Department or faculty (optional)
- `is_instructor` - Whether user can create/manage courses
- `google_id` - Google OAuth ID (for Google sign-in)

### Authentication Setup

1. Ensure your `.env` file includes:
```ini
# Django's secret key for general Django operations
SECRET_KEY=django-insecure-replace-this-with-a-better-key

# For development, you can use the same key as SECRET_KEY
# For production, use a different strong random key
JWT_SECRET_KEY=your-jwt-secret-key

# Google OAuth credentials
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

2. For Google OAuth, set up a project in Google Cloud Console and add the credentials to your `.env` file.

### Secret Key Management

The application uses two types of secret keys:

1. `SECRET_KEY`: Django's built-in secret key used for:
   - Session security
   - CSRF protection
   - Password reset tokens
   - Other Django-specific cryptographic operations

2. `JWT_SECRET_KEY`: Used specifically for signing and verifying JSON Web Tokens (JWT)
   - Currently defaults to `SECRET_KEY` if not set
   - In production, it's recommended to use a different key for better security
   - Can be generated using Python's secrets module:
     ```python
     import secrets
     print(secrets.token_urlsafe(50))  # Generates a secure random key
     ```

> **Note**: While using the same key for both Django and JWT operations works, it's recommended to use separate keys in production for better security. The application will work with either setup.

📂 Project Structure (key folders)
```bash
learnmore_reborn/
├── courses/
│   ├── models.py           # Course, Module, Quiz, Question models
│   ├── serializers.py      # Course, Quiz, Question serializers
│   ├── views.py            # Core course views
│   ├── api_views.py        # Course API endpoints
│   ├── quiz_views.py       # Quiz API endpoints
│   ├── module_quiz_views.py # Module quiz integration
│   ├── admin.py
│   ├── apps.py
│   ├── tests/              # Test directory
│   │   ├── test_models.py
│   │   ├── test_quiz_model.py
│   │   └── ...
│   ├── templates/
│   │   ├── courses/
│   │   │   ├── quiz-detail.html
│   │   │   ├── quiz-list.html
│   │   │   └── ...
│   └── migrations/
├── progress/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── api_views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests/
│   └── migrations/
├── users/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests/
│   └── migrations/
├── analytics/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── ai_tutor/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── learnmore/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
├── requirements.txt
├── manage.py
```