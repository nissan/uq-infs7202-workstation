# Getting Started with LearnMore Plus

This guide will help you set up the development environment for LearnMore Plus.

## Initial Setup

1. Create a new directory for the project:
   ```bash
   mkdir learnmore-plus
   cd learnmore-plus
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Django and other dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```

4. Create a new Django project:
   ```bash
   django-admin startproject learnmore_plus .
   ```

5. Create the necessary apps:
   ```bash
   python manage.py startapp accounts
   python manage.py startapp courses
   ```

## Project Structure

Set up the following directory structure:
```
learnmore_plus/
├── accounts/
│   ├── migrations/
│   ├── templates/
│   │   └── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── courses/
│   ├── migrations/
│   ├── templates/
│   │   └── courses/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   └── components/
├── learnmore_plus/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── .env
```

## Configuration

1. Update settings.py:
   - Add apps to INSTALLED_APPS
   - Configure database
   - Set up static files
   - Configure templates
   - Add authentication settings

2. Create .env file:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/learnmore
   ```

3. Set up Tailwind CSS:
   ```bash
   npm init -y
   npm install -D tailwindcss
   npx tailwindcss init
   ```

## Next Steps

1. Set up version control:
   ```bash
   git init
   git add .
   git commit -m "Initial project setup"
   ```

2. Create initial documentation:
   - README.md
   - TODO.md
   - NOTES.md
   - CHECKPOINT.md

3. Start development:
   - Implement user authentication
   - Create course models
   - Set up templates
   - Add static files

## Development Workflow

1. Create a new branch for each feature
2. Write tests before implementation
3. Follow PEP 8 style guide
4. Document changes
5. Create pull requests for review

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Troubleshooting

1. Database issues:
   - Check database connection settings
   - Verify migrations are applied
   - Check for conflicting migrations

2. Static files not loading:
   - Verify STATIC_URL and STATIC_ROOT settings
   - Run collectstatic
   - Check file permissions

3. Template issues:
   - Verify template directories in settings
   - Check template inheritance
   - Verify template tags

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [django-allauth Documentation](https://django-allauth.readthedocs.io/) 