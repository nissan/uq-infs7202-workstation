# Getting Started with Enhanced LearnMore

## Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis (for caching)
- Git

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/enhanced-learnmore.git
cd enhanced-learnmore/djangoapps/learnmore_plus
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# For development environment
pip install -r requirements/dev.txt

# For production environment
pip install -r requirements/prod.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up the database:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Seed demo data (optional):
```bash
python manage.py reset_db  # This will reset the database and seed all demo data
# Or seed individual components:
python manage.py seed_demo_data
python manage.py seed_ai_tutor_demo
```

8. Set up AI Tutor functionality (optional):
```bash
# Install required LangChain packages for AI Tutor
pip install langchain-core langchain-community
pip install langchain-openai  # For OpenAI integration
pip install langchain-ollama  # For Ollama integration
pip install langchain-huggingface  # For HuggingFace embeddings
pip install langchain-chroma  # For vector storage

# Index course content for the AI tutor
python manage.py index_course_content

# For local LLM support, install Ollama from https://ollama.ai/ and run:
ollama pull llama3
ollama pull nomic-embed-text  # REQUIRED for embedding content
ollama serve

# Alternatively, configure OpenAI in your .env:
# OPENAI_API_KEY=your_api_key_here
# DEFAULT_LLM_MODEL=gpt-3.5-turbo
```

**Important**: The `nomic-embed-text` model is required for content indexing with Ollama. Without this model, the AI tutor will fall back to local HuggingFace embeddings, which may affect performance.

9. Run the development server:
```bash
python manage.py runserver
```

## Accessing the System

### Admin Interfaces
1. System Admin Dashboard: `http://localhost:8000/dashboard/`
   - Overview of system statistics
   - Quick access to user management
   - Recent activity monitoring
   - Direct links to Django admin interface

2. Django Admin Interface: `http://localhost:8000/admin/`
   - Detailed user management
   - Database-level operations
   - Advanced system configuration
   - Complete model management

### Key Features

1. AI Tutor System: `http://localhost:8000/tutor/`
   - Intelligent tutoring with LLM integration
   - Context-aware responses using RAG (Retrieval Augmented Generation)
   - Course, module, and content-specific tutoring
   - Session management with conversation history
   - Three-panel responsive interface

2. QR Code System: Access via course detail pages
   - QR code generation for courses and modules
   - Scan tracking and analytics
   - Printable QR sheet generation

3. Course Management: `http://localhost:8000/courses/`
   - Course creation and editing
   - Module and content organization
   - Student enrollment and progress tracking
   - Learning interface with progress tracking

### Demo Users
After running `python manage.py seed_demo_data`, you can use these accounts:

#### Admins
- Username: `admin`
- Password: `admin123`
- Email: admin@example.com

#### Course Coordinators
- Username: `coordinator`
- Password: `coordinator123`
- Email: coordinator@example.com

#### Instructors
- Username: `dr.smith`
- Password: `dr.smith123`
- Email: dr.smith@example.com

#### Students
- Username: `john.doe`
- Password: `john.doe123`
- Email: john@example.com

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

### Project Structure
- `apps/` - Django applications
  - `accounts/` - User management
  - `core/` - Core functionality
  - `courses/` - Course management
  - `dashboard/` - Admin dashboard
  - `qr_codes/` - QR code functionality
  - `ai_tutor/` - AI Tutor system
- `templates/` - Base templates
- `static/` - Static files
- `media/` - User-uploaded files
- `learnmore_plus/` - Project settings
- `docs/` - Project documentation

### Key Components

#### AI Tutor System
- `apps/ai_tutor/models.py` - Data models for sessions, messages, and context
- `apps/ai_tutor/services.py` - Service layer with LLM integration and RAG
- `apps/ai_tutor/views.py` - View logic for tutor interface
- `templates/ai_tutor/` - UI templates for tutor interface

#### Course System
- `apps/courses/models.py` - Course, Module, Content models
- `apps/courses/views.py` - Course management views
- `apps/courses/quiz_views.py` - Quiz functionality

#### QR Code System
- `apps/qr_codes/models.py` - QR code models
- `apps/qr_codes/services.py` - QR code generation and tracking

### Git Workflow
1. Create a new branch for each feature
2. Make small, focused commits
3. Write clear commit messages
4. Submit pull requests for review

### Testing
- Write tests for new features
- Run tests before committing
- Maintain test coverage
- Document test cases

### Documentation
- Keep README.md updated
- Document API changes
- Update user guides
- Maintain development notes
- Update START.md for new developers

## Common Issues

### Database Connection
- Ensure PostgreSQL is running
- Check database credentials in .env
- Verify database exists

### Static Files
- Run `python manage.py collectstatic`
- Check STATIC_ROOT setting
- Verify static files directory

### Admin Access
- Ensure user is in admin group
- Check user permissions
- Verify login credentials

### Import Errors
- If you see errors like `ModuleNotFoundError: No module named 'courses'`, check import paths in management commands
- Make sure to use `from apps.courses.models` instead of `from courses.models` in the `apps` directory
- For module resolution issues, try running the command with a full path:
  ```bash
  PYTHONPATH=/Users/nissan/code/uq-infs7202-workstation/djangoapps/learnmore_plus python manage.py reset_db
  ```

### AI Tutor Issues
- Verify Ollama is running (`ollama serve`) for local development
- Check OpenAI API key if using cloud LLM
- Run content indexing if no context is retrieved (`python manage.py index_course_content`)
- Check vector database path is writable
- Ensure LLM-related settings are configured in .env or settings

If you get errors like "no such table: ai_tutor_tutorsession" when running the seeding commands:
```bash
# Run the fix script
./fix_ai_tutor.sh

# Or manually run these commands:
python manage.py makemigrations ai_tutor
python manage.py migrate ai_tutor
python manage.py setup_groups
python manage.py create_test_users
python manage.py seed_ai_tutor_demo
python manage.py index_course_content
```

### QR Code Generation
- Ensure media directory is writable
- Check QR code settings in .env
- Verify PIL/Pillow is installed correctly

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue
4. Contact the development team
