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

# Create a non-root user
RUN useradd -m appuser

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app/staticfiles

# Switch to non-root user
USER appuser

# Default command (can be overridden by railway.toml startCommand)
CMD ["gunicorn", "learnmore.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--threads", "8", "--timeout", "0"] 