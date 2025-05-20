# Deploying to Railway.app

This document provides step-by-step instructions for deploying the LearnMore Plus application to Railway.app.

> **Config-as-Code Available**: We've implemented a `railway.toml` file for automated deployment. See [Railway Config as Code](railway-config-as-code.md) for details on this simpler approach.

## Prerequisites

Before deploying to Railway, ensure you have:

1. A Railway.app account (sign up at [railway.app](https://railway.app))
2. Railway CLI installed (optional but recommended)
3. Git repository set up and code committed
4. Project properly configured for production

## Required Configuration Files

Ensure these files are properly set up in your project:

1. **Procfile** - Tells Railway how to run your application
2. **requirements.txt** - Lists all Python dependencies
3. **runtime.txt** - Specifies the Python version
4. **production settings** - Production-ready Django settings

## Configuration File Setup

### 1. Procfile

Create a `Procfile` (no extension) in the project root:

```
web: gunicorn learnmore_plus.wsgi:application --log-file -
release: python manage.py migrate
```

This tells Railway to:
- Run the application using Gunicorn
- Automatically run migrations before each deployment

### 2. requirements.txt

Consolidate your requirements for production:

```bash
# Generate a single requirements file for Railway
pip freeze > requirements.txt

# Or manually create a comprehensive requirements file
cat requirements/base.txt requirements/prod.txt > requirements.txt
```

Ensure these critical packages are included:
```
django>=4.2.0,<4.3.0
gunicorn>=21.2.0
whitenoise>=6.5.0
psycopg2-binary>=2.9.6
dj-database-url>=2.1.0
django-environ>=0.11.2
```

### 3. runtime.txt

Specify the Python version:

```
python-3.11.6
```

### 4. Production Settings

Ensure your `learnmore_plus/settings/prod.py` file is configured correctly:

```python
import os
import dj_database_url
from .base import *

# SECURITY
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', '')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.UserActivityMiddleware',
]

# DATABASE
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# STATIC FILES
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email settings (if using Railway email add-on or external provider)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# AI Tutor settings for production
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
DEFAULT_LLM_MODEL = os.environ.get('DEFAULT_LLM_MODEL', 'gpt-3.5-turbo')
```

## Deployment Steps

### 1. Deploy from GitHub

The easiest way to deploy is directly from your GitHub repository:

1. Log in to Railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Click "Deploy Now"

### 2. Configure Environment Variables

Configure the following environment variables in Railway's dashboard:

```
DJANGO_SETTINGS_MODULE=learnmore_plus.settings.prod
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-railway-app-url.railway.app,your-custom-domain.com
OPENAI_API_KEY=your-openai-api-key (if using OpenAI for AI Tutor)
```

Railway automatically provides:
- `DATABASE_URL` (if you add a PostgreSQL database)
- `PORT` (for the web server)

### 3. Add PostgreSQL Database

1. In your project dashboard, click "New" → "Database" → "PostgreSQL"
2. Wait for the database to provision
3. Railway will automatically add the `DATABASE_URL` environment variable

### 4. Set Up Domain (Optional)

1. In project "Settings" → "Domains"
2. Use the provided Railway subdomain or add a custom domain
3. If using a custom domain, configure DNS settings as instructed

### 5. Generate New Secret Key

Generate a new Django secret key for production:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Add this generated key to your Railway environment variables.

### 6. Deploy and Monitor

1. Railway will automatically detect your `Procfile` and deploy your application
2. Monitor the deployment logs for any errors
3. Once deployed, Railway will provide you with a URL to access your application

## Post-Deployment Tasks

### 1. Collect Static Files

Railway should collect static files automatically based on your `Procfile`, but if needed:

1. Navigate to project "Settings" → "Shell"
2. Run: `python manage.py collectstatic --no-input`

### 2. Create Superuser

Create an admin user for your production instance:

1. Navigate to project "Settings" → "Shell"
2. Run: `python manage.py createsuperuser`
3. Follow the prompts to create an admin account

### 3. Seed Demo Data (Optional)

If you want to add demo data to your production instance:

1. Navigate to project "Settings" → "Shell"
2. Run: `python manage.py reset_db`
3. Or for AI Tutor demo data: `python manage.py seed_ai_tutor_demo`

### 4. Monitor Application

1. Watch application logs in Railway dashboard
2. Configure health checks
3. Monitor database usage

## Railway CLI Usage (Optional)

You can also use the Railway CLI for deployment:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy your application
railway up

# Run commands on your deployed instance
railway run python manage.py migrate
railway run python manage.py createsuperuser

# View logs
railway logs
```

## Troubleshooting

### Common Issues and Fixes

1. **Database Migration Errors**
   - Check migration files for compatibility issues
   - Use Railway shell to run migrations manually

2. **Static Files Not Loading**
   - Ensure `STATIC_ROOT` is set correctly
   - Run `collectstatic` manually
   - Verify WhiteNoise is configured correctly

3. **Application Error or 500 Responses**
   - Check application logs in Railway dashboard
   - Verify environment variables are set correctly
   - Ensure databases are properly configured

4. **High CPU or Memory Usage**
   - Optimize database queries
   - Configure caching if needed
   - Scale up resources in Railway dashboard

## Continuous Deployment

Railway supports automatic deployments whenever you push to your connected GitHub repository:

1. Ensure your repository is connected to Railway
2. Push changes to your main branch
3. Railway will automatically deploy your changes

## Scaling

As your application grows:

1. Upgrade your Railway plan as needed
2. Add multiple instances of your application for high availability
3. Configure a CDN for static assets
4. Use database read replicas for high traffic scenarios

## Maintenance Mode

If you need to take your site offline temporarily:

1. Add a `MAINTENANCE_MODE=True` environment variable
2. Update your `settings/prod.py` to check for this variable
3. Add middleware to show a maintenance page when the variable is set

## Backup Strategy

Regularly back up your database:

1. Set up scheduled backups in Railway PostgreSQL settings
2. Consider additional external backup solutions for critical data
3. Test database restoration procedures periodically

## Security Recommendations

1. Keep your `SECRET_KEY` secure and different from development
2. Enable all security settings in your production settings
3. Regularly update dependencies for security patches
4. Use strong passwords for all admin accounts
5. Implement rate limiting for login and critical endpoints
6. Consider adding Two-Factor Authentication for admin users

## Cost Management

Railway charges based on usage:

1. Monitor database and application resource usage
2. Scale down when not needed
3. Use Railway's usage-based billing to optimize costs
4. Set up usage alerts to avoid unexpected charges

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/)