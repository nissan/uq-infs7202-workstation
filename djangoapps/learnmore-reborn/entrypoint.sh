#!/bin/bash
set -e

echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Environment variables:"
env | sort

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin user if needed..."
python -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@learnmore.com', '${DJANGO_ADMIN_PASSWORD}')"

echo "Starting Gunicorn on port $PORT..."
exec gunicorn learnmore.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0 --log-level debug 