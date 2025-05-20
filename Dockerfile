# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=learnmore.settings \
    PORT=8080 \
    SECRET_KEY=django-insecure-test-key-for-local-development-only \
    DEBUG=True \
    ALLOWED_HOSTS=localhost,127.0.0.1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY djangoapps/learnmore-reborn/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY djangoapps/learnmore-reborn .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app

# Add healthcheck (before switching to non-root user)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:$PORT/admin/ || exit 1

USER appuser

# Run migrations, collect static files, and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn learnmore.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 0"] 