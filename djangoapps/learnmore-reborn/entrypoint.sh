#!/bin/bash
set -ex  # Add -x for verbose output and -e to exit on error

echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Environment variables:"
env | sort

echo "Checking Python and Django installation..."
python --version
python -c "import django; print(f'Django version: {django.__version__}')"

echo "Checking database connection..."
python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('Database connection successful')"

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput --verbosity 2

echo "Creating admin user if needed..."
python -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating admin user...')
    User.objects.create_superuser('admin', 'admin@learnmore.com', '${DJANGO_ADMIN_PASSWORD}')
    print('Admin user created successfully')
else:
    print('Admin user already exists')
"

echo "Starting Gunicorn on port $PORT..."
exec gunicorn learnmore.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0 --log-level debug --access-logfile - --error-logfile - 