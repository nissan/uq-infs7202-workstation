# LearnMore Docker Demo Environment

This guide explains how to use Docker to quickly set up a self-contained demo environment for the LearnMore platform.

## 🐳 Quick Start with Docker

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

### Option 1: Using Docker Compose (Recommended)

The easiest way to start the demo environment is with Docker Compose:

```bash
# Start the container
docker-compose up

# Access the platform at http://localhost:8000
```

That's it! Docker Compose will:
1. Build the Docker image
2. Start the container
3. Run migrations
4. Create test users
5. Generate demo course content
6. Set up the AI tutor with RAG integration
7. Start the Django development server

### Option 2: Using Docker Directly

If you prefer to use Docker commands directly:

```bash
# Build the image
docker build -t learnmore-demo .

# Run the container
docker run -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/media:/app/media learnmore-demo
```

## 🧑‍💻 Demo User Accounts

The following accounts are available for testing different roles:

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Admin | admin | testpass123 | admin@example.com |
| Instructor | professor | testpass123 | professor@example.com |
| Instructor | teacher | testpass123 | teacher@example.com |
| Student | student1 | testpass123 | student1@example.com |
| Student | student2 | testpass123 | student2@example.com |
| Student | student3 | testpass123 | student3@example.com |

## 🧪 Demo Features

The Docker demo environment includes all features from the standard demo:

1. **Course Catalog & Enrollment**
2. **Advanced Quiz System** with multiple question types
3. **AI Tutor with RAG Integration** using course content
4. **Analytics Dashboards** for students and instructors

For more details on the features, see the main [README_DEMO.md](README_DEMO.md).

## 🛠️ Container Management

### View Container Logs

```bash
# With Docker Compose
docker-compose logs -f

# With Docker
docker logs <container_id>
```

### Enter the Container Shell

```bash
# With Docker Compose
docker-compose exec learnmore bash

# With Docker
docker exec -it <container_id> bash
```

### Stop the Container

```bash
# With Docker Compose
docker-compose down

# With Docker
docker stop <container_id>
```

### Reset Container Data

To completely reset the demo data:

```bash
# Remove volumes and containers
docker-compose down -v

# Remove any leftover data directories
rm -rf data media

# Start fresh
docker-compose up
```

## 📊 Persistence

The Docker setup uses volumes to persist data between container restarts:

- **Database**: Stored in the `./data` directory
- **Media Files**: Stored in the `./media` directory

This means your demo environment state is preserved even if you restart the container.

## 🔄 Custom Configuration

### Using Environment Variables

You can customize the environment by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - DJANGO_SETTINGS_MODULE=learnmore.settings
  - DJANGO_SUPERUSER_USERNAME=customadmin
  - DJANGO_SUPERUSER_PASSWORD=custompassword
  - DJANGO_SUPERUSER_EMAIL=custom@example.com
```

### Using a Custom Settings File

For more advanced customization, you can mount a custom settings file:

```yaml
volumes:
  - ./custom_settings.py:/app/learnmore/settings_local.py
```

Then update the `DJANGO_SETTINGS_MODULE` environment variable:

```yaml
environment:
  - DJANGO_SETTINGS_MODULE=learnmore.settings_local
```

## 🚀 Next Steps

After exploring the demo, you might want to:

1. **Customize the Demo Content**: Edit the `create_demo_rag_content.py` script
2. **Extend the AI Tutor**: Enhance the RAG integration in `ai_tutor/rag_integration.py`
3. **Add Real API Keys**: Replace mock embeddings with real OpenAI API keys for production use

## ⚠️ Production Considerations

This Docker setup is optimized for demonstration purposes. For production deployments, consider:

1. Using a production-ready web server (Gunicorn, uWSGI)
2. Setting up a proper database (PostgreSQL, MySQL)
3. Implementing HTTPS with a reverse proxy (Nginx, Caddy)
4. Adding proper security configurations
5. Setting up proper API keys for third-party services