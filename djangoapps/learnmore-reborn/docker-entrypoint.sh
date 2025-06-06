#!/bin/bash
set -e

# Function to check if PostgreSQL is ready
postgres_ready() {
    python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT:-5432}"
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for PostgreSQL if using PostgreSQL
if [[ "$DATABASE_URL" == postgres* ]]; then
    until postgres_ready; do
        >&2 echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    >&2 echo "PostgreSQL is up - executing command"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create a health check endpoint
echo "Creating health check endpoint..."
cat > /app/health/views.py << EOF
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db import connection

@csrf_exempt
def health_check(request):
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        return HttpResponse("Database check failed: {}".format(str(e)), status=503)

    # Check cache
    try:
        cache.set("health_check", "ok", 1)
        if cache.get("health_check") != "ok":
            raise Exception("Cache get/set failed")
    except Exception as e:
        return HttpResponse("Cache check failed: {}".format(str(e)), status=503)

    return HttpResponse("ok", content_type="text/plain")
EOF

# Add health check URL
echo "Adding health check URL..."
cat >> /app/learnmore/urls.py << EOF

# Health check endpoint
from health.views import health_check
urlpatterns += [path("health/", health_check, name="health_check"),]
EOF

# Run the setup script to initialize the demo environment
echo "Setting up demo environment..."
chmod +x /app/setup_demo_env.sh
/app/setup_demo_env.sh

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create media directory if it doesn't exist
mkdir -p /app/media

# Set proper permissions
chmod -R 755 /app/data /app/media /app/staticfiles


# Start Gunicorn
echo "Starting Gunicorn..."
exec "$@"