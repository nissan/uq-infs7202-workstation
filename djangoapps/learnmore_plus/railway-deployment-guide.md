# Railway.app Deployment Guide for LearnMore Plus

This guide outlines the steps to deploy the LearnMore Plus Django application to Railway.app.

## Pre-Deployment Setup

### 1. Create a requirements.txt file

Your project already has requirements split into base.txt, dev.txt, and prod.txt. We need to create a consolidated requirements.txt file for Railway.

```bash
# In the root directory of learnmore_plus
cat requirements/prod.txt > requirements.txt
```

This will use your production requirements, which already include gunicorn.

### 2. Create a Procfile

Create a file named `Procfile` (with capital P and no extension) in the root directory of the learnmore_plus project.

```
web: gunicorn learnmore_plus.wsgi --log-file -
```

### 3. Set up Static Files

Ensure your static files configuration is set properly in the production settings. Add or modify the following in `learnmore_plus/settings/prod.py`:

```python
# Static files settings
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Simplified static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Whitenoise middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... rest of your middleware classes
]
```

### 4. Update Database Configuration in Production Settings

Ensure your production settings handle the database URL correctly:

```python
# In learnmore_plus/settings/prod.py

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}
```

Make sure to install dj_database_url by adding it to requirements.txt:

```
dj-database-url==2.1.0
```

### 5. Create a runtime.txt file

Create a runtime.txt file to specify the Python version:

```
python-3.11.7
```

## Railway Deployment Steps

### 1. Push to GitHub

Commit and push your updated code to GitHub:

```bash
git add Procfile requirements.txt runtime.txt
git commit -m "Add Railway deployment files"
git push
```

### 2. Set up Railway Project

1. Create a new project in Railway.app
2. Connect your GitHub repository
3. Add PostgreSQL plugin from the Railway dashboard

### 3. Configure Railway Deployment

1. Set the root directory to the learnmore_plus project folder
2. Configure environment variables in Railway → Variables:

```
DJANGO_SETTINGS_MODULE=learnmore_plus.settings.prod
DJANGO_SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=.railway.app
```

3. If you're using AI features with OpenAI, add:

```
OPENAI_API_KEY=<your-api-key>
```

4. For the QR code service, set any required environment variables.

### 4. Deploy Application

1. Railway will automatically deploy your application
2. After deployment, go to the "Settings" tab to get your application URL

### 5. Post-Deployment Tasks

1. Run migrations:

```bash
railway run python manage.py migrate
```

2. Create a superuser:

```bash
railway run python manage.py createsuperuser
```

3. Load initial data:

```bash
railway run python manage.py seed_demo_data
railway run python manage.py create_test_users
railway run python manage.py setup_groups
railway run python manage.py setup_roles
```

4. Set up static files:

```bash
railway run python manage.py collectstatic --noinput
```

## Troubleshooting

### PostgreSQL Connection Issues

If you have trouble connecting to the PostgreSQL database, verify that the DATABASE_URL environment variable is set correctly in Railway and that your settings file is properly configured to use it.

### Static Files Not Loading

If static files aren't being served properly:

1. Ensure the whitenoise middleware is in the correct position (after django.middleware.security.SecurityMiddleware)
2. Run collectstatic again
3. Check if the static files are included in the build

### Application Errors

Check the application logs in Railway:

1. Go to your project in Railway
2. Click on "Deployments"
3. Select your latest deployment
4. Click on "Logs" to see what's happening

## Monitoring

Set up monitoring to keep track of your application's health:

1. Railway provides basic logs and metrics
2. Consider integrating Sentry for error tracking

## Notes Specific to LearnMore Plus

1. **AI Tutor Features**: The AI tutor requires either Ollama or OpenAI. For Railway deployment, OpenAI is recommended as Ollama requires additional setup.

2. **Vector Database**: The vector database for AI features uses disk storage by default. Ensure this works in Railway or consider using a cloud-based alternative.

3. **Media Files**: Configure Django Storages with AWS S3 or similar for media file storage in production.

4. **Session Handling**: By default, sessions are stored in the database. For better performance, consider using Redis for session storage.

5. **Performance Optimization**: Once deployed, monitor performance and consider adding caching where appropriate.