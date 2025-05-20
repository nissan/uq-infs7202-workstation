#!/bin/bash
set -ex  # Add -x for verbose output and -e to exit on error

# Function to check if a required environment variable is set
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "Error: Required environment variable $1 is not set"
        exit 1
    fi
}

# Function to run a command and check its status
run_command() {
    echo "Running: $1"
    eval "$1"
    if [ $? -ne 0 ]; then
        echo "Error: Command failed: $1"
        exit 1
    fi
}

echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Check only essential environment variables
echo "Checking required environment variables..."
check_env_var "DATABASE_URL"
check_env_var "DJANGO_SECRET_KEY"
check_env_var "ALLOWED_HOSTS"

echo "Environment variables:"
env | sort

echo "Checking Python and Django installation..."
run_command "python --version"
run_command "python -c \"import django; print(f'Django version: {django.__version__}')\""

echo "Checking database connection..."
run_command "python -c \"
import os
import sys
import django
from django.db import connection
from django.db.utils import OperationalError

try:
    django.setup()
    connection.ensure_connection()
    print('Database connection successful')
except OperationalError as e:
    print(f'Database connection failed: {e}')
    print(f'DATABASE_URL: {os.environ.get(\"DATABASE_URL\", \"not set\")}')
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error during database connection: {e}')
    sys.exit(1)
\""

echo "Running migrations..."
run_command "python manage.py migrate"

echo "Collecting static files..."
run_command "python manage.py collectstatic --noinput --verbosity 2"

# Only attempt to create admin user if DJANGO_ADMIN_PASSWORD is set
if [ -n "${DJANGO_ADMIN_PASSWORD}" ]; then
    echo "Creating admin user..."
    run_command "python -c \"
import os
import sys
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

try:
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        print('Creating admin user...')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD')
        User.objects.create_superuser('admin', 'admin@learnmore.com', password)
        print('Admin user created successfully')
    else:
        print('Admin user already exists')
except OperationalError as e:
    print(f'Database error during admin user creation: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error during admin user creation: {e}')
    sys.exit(1)
\""
else
    echo "Skipping admin user creation (DJANGO_ADMIN_PASSWORD not set)"
fi

echo "Checking static files..."
run_command "python -c \"
import os
from django.conf import settings
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATIC_ROOT exists: {os.path.exists(settings.STATIC_ROOT)}')
print(f'STATIC_ROOT contents: {os.listdir(settings.STATIC_ROOT) if os.path.exists(settings.STATIC_ROOT) else \"Directory not found\"}')
\""

echo "Starting Gunicorn on port $PORT..."
echo "Gunicorn command: gunicorn learnmore.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0 --log-level debug --access-logfile - --error-logfile -"
exec gunicorn learnmore.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0 --log-level debug --access-logfile - --error-logfile - 