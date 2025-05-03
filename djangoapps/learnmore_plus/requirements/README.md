# Requirements Management

This directory contains the project's Python package requirements, organized by environment:

- `base.txt`: Core dependencies required in all environments
- `dev.txt`: Development-specific dependencies (testing, linting, etc.)
- `prod.txt`: Production-specific dependencies (WSGI server, monitoring, etc.)

## Usage

### Development Environment
```bash
pip install -r requirements/dev.txt
```

### Production Environment
```bash
pip install -r requirements/prod.txt
```

## Structure

### Base Requirements
- Django and core dependencies
- Authentication (django-allauth)
- Frontend tools (Tailwind, SASS)
- API tools (DRF, Swagger)
- Database adapters
- Security packages

### Development Requirements
- Debug toolbar
- Code formatting (black, isort)
- Linting (flake8)
- Testing (pytest, coverage)
- Test data generation (factory-boy, faker)

### Production Requirements
- WSGI server (gunicorn)
- File storage (django-storages)
- Monitoring (sentry-sdk)
- Caching (redis)
- Task queue (celery)
- Scheduled tasks (celery-beat) 