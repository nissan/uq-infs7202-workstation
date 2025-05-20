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

## 🔐 Authentication & Profile Management

The application uses Django's built-in User model with a custom UserProfile extension for additional user information. Authentication is handled through JWT tokens.

## 📚 Course Catalog & Enrollment

The platform features a comprehensive course catalog with enrollment management capabilities. Users can browse courses, filter by enrollment type, search for specific courses, and enroll in courses of interest.

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
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── progress/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── users/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
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