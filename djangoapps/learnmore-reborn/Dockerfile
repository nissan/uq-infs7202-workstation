# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=learnmore.settings \
    PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set up staticfiles directory with proper permissions
RUN mkdir -p /app/staticfiles && chmod 755 /app/staticfiles

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a non-root user and set permissions
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/staticfiles

# Switch to non-root user
USER appuser

# Create a script to handle startup tasks
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin user if it doesn't exist
python -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@learnmore.com', '${DJANGO_ADMIN_PASSWORD}')"

# Start Gunicorn
exec gunicorn learnmore.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0
EOF

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"] 