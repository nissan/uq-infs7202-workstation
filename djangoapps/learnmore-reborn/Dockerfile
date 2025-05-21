# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=learnmore.settings \
    PATH="/opt/venv/bin:$PATH" \
    # Security
    PYTHONHASHSEED=random \
    # Gunicorn
    GUNICORN_CMD_ARGS="--workers=1 --bind=0.0.0.0:8000 --timeout=60 --access-logfile=- --error-logfile=- --capture-output --log-level=info"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /opt/venv/lib/python3.11/site-packages

# Copy project files and .env file
COPY --chown=appuser:appuser . .

# Create required directories with proper permissions
RUN mkdir -p /app/data /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Make the entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Create a non-root user to run the application
RUN mkdir -p /home/appuser/.cache/pip \
    && chown -R appuser:appuser /home/appuser/.cache

# Expose the port the app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Set the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["gunicorn", "learnmore.wsgi:application"]
