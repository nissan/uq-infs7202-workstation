# Railway Configuration as Code

This document explains how to use the `railway.toml` file to automate and standardize our deployment to Railway.app.

## Overview

Railway's Configuration as Code (Railway Config) allows us to define our deployment configuration in a `railway.toml` file at the root of our project. This provides several benefits:

1. **Version-controlled infrastructure**: All configuration changes are tracked in Git
2. **Consistent deployments**: Ensures the same configuration is used for all deployments
3. **Automated setup**: Reduces manual configuration in the Railway dashboard
4. **Self-documenting**: The configuration file serves as documentation for the deployment

## The `railway.toml` File

We've created a `railway.toml` file in the project root with the following sections:

### Build Configuration

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"
```

This section tells Railway how to build our application:
- Uses Nixpacks for the build process
- Installs dependencies from requirements.txt

### Deploy Configuration

```toml
[deploy]
startCommand = "gunicorn learnmore_plus.wsgi:application"
healthcheckPath = "/health/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 5

[deploy.lifecycle]
type = "single"
```

This section configures the deployment process:
- Defines the command to start the application
- Sets up health checks at the `/health/` endpoint
- Configures automatic restarts if the application fails
- Uses a single-instance lifecycle model

### Service Configuration

```toml
[service]
internal_port = 8000
checkConnection = true
protocol = "http"
healthcheck_enabled = true
healthcheck_timeout = 30

[service.commands]
[service.commands.release]
command = "python manage.py migrate"

[service.vars]
DJANGO_SETTINGS_MODULE = "learnmore_plus.settings.prod"
PYTHON_VERSION = "3.11.6"
APP_NAME = "learnmore-plus"
PYTHONUNBUFFERED = "1"
```

This section defines how the service runs:
- Sets the internal port to 8000
- Enables health checks
- Runs database migrations on release
- Sets environment variables for Django

### Scaling Configuration

```toml
[service.scaling]
min_instances = 1
max_instances = 3
depends_on = ["${{ Database }}", "${{ Redis }}"]
```

This section configures auto-scaling:
- Minimum of 1 instance
- Maximum of 3 instances
- Depends on the database and Redis services

### Database Configuration

```toml
[[database]]
plan = "shared"
name = "postgres"
```

This section defines the PostgreSQL database:
- Uses the shared plan
- Names the service "postgres"

### Redis Configuration

```toml
[[redis]]
plan = "starter"
name = "cache"
```

This section defines the Redis cache:
- Uses the starter plan
- Names the service "cache"

## Required Django Configuration

To support the Railway configuration, we've added:

1. **Health Check Endpoint**: A simple endpoint at `/health/` that returns "OK" when the application is healthy.

2. **Metrics Endpoint**: An endpoint at `/metrics/` that returns Prometheus-formatted metrics about the application.

These endpoints are defined in:
- `learnmore_plus/urls.py` for the health check
- `apps/core/views_monitoring.py` for the metrics endpoint

## How to Deploy with Railway Config

1. **Deploy via GitHub**:
   - Push your code with the `railway.toml` file to GitHub
   - In Railway dashboard, click "New Project" → "Deploy from GitHub"
   - Select your repository
   - Railway will automatically detect and use the `railway.toml` configuration

2. **Deploy via CLI**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli

   # Login to Railway
   railway login

   # Initialize project (first time only)
   railway init

   # Deploy your application
   railway up
   ```

3. **Environment Variables in Dashboard**:
   Some sensitive environment variables should still be set in the Railway dashboard:
   - `SECRET_KEY`: Your Django secret key
   - `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
   - `OPENAI_API_KEY`: API key for OpenAI (if using it for AI Tutor)

## Monitoring and Scaling

The configuration enables:

1. **Health Checks**: Railway will periodically check the `/health/` endpoint to ensure your application is running correctly.

2. **Metrics**: The `/metrics/` endpoint provides Prometheus-formatted metrics that can be used with Railway's monitoring.

3. **Auto-scaling**: The application will automatically scale between 1 and 3 instances based on load.

## Database Migrations

Database migrations run automatically as part of the release process:

```toml
[service.commands.release]
command = "python manage.py migrate"
```

This ensures your database schema is always up to date with your code.

## Troubleshooting

If you encounter issues with Railway Config deployment:

1. **Check the build logs** for any errors during the build process.

2. **Verify health checks** are passing by checking the `/health/` endpoint.

3. **Review environment variables** to ensure all required variables are set correctly.

4. **Inspect the metrics endpoint** at `/metrics/` to see if the application is functioning properly.

## Reverting to Manual Configuration

If you need to disable Railway Config temporarily:

1. In the Railway dashboard, go to your project settings
2. Under "Deployment Method", click "Edit"
3. Choose "Manual Configuration"
4. This will ignore the `railway.toml` file for the current deployment

## Further Reading

For more information on Railway Config:
- [Railway Configuration as Code Documentation](https://docs.railway.app/reference/config-as-code)
- [Railway TOML Reference](https://docs.railway.app/reference/config-as-code#configurable-settings)
- [Railway Nixpacks Documentation](https://docs.railway.app/guides/nixpacks)