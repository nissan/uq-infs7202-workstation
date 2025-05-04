# Enhanced LearnMore

A Django-based learning management system with AI-powered learning tools for educators and students worldwide.

## Quick Start

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

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Reset and seed the database with demo data:
```bash
python manage.py reset_db
```
This command will:
- Flush the existing database
- Run all migrations
- Set up groups and permissions
- Seed demo data including users, courses, and activity logs
- Display test user credentials

7. For AI Tutor functionality (optional):
```bash
# First, install required LangChain packages:
pip install langchain-core langchain-community
pip install langchain-openai langchain-ollama langchain-huggingface langchain-chroma

# For local LLM support, install Ollama from https://ollama.ai/ and run:
ollama pull llama3
ollama pull nomic-embed-text  # REQUIRED for embedding functionality
ollama serve

# Alternatively, configure OpenAI for production:
export OPENAI_API_KEY=your_api_key_here
```

The easiest way to set up the AI Tutor is to use our automated fix script:
```bash
chmod +x fix_ai_tutor.sh
./fix_ai_tutor.sh
```

This script will automatically:
- Reset the database and run all migrations
- Create and apply AI tutor-specific migrations
- Set up groups and users
- Seed AI tutor demo data
- Index course content for RAG retrieval
- Fix common issues like import paths automatically

### Troubleshooting AI Tutor Setup

If you encounter these common issues, here are the fixes:

1. **"No such table: ai_tutor_tutorsession" error**:
   ```bash
   python manage.py makemigrations ai_tutor
   python manage.py migrate ai_tutor
   python manage.py seed_ai_tutor_demo
   python manage.py index_course_content
   ```

2. **"ModuleNotFoundError: No module named 'courses'"**:
   This is an import path issue. All imports should use the "apps." prefix:
   ```bash
   # Set PYTHONPATH to include the project root
   PYTHONPATH=/path/to/djangoapps/learnmore_plus python manage.py reset_db
   
   # Or use the fix script which handles paths correctly
   ./fix_ai_tutor.sh
   ```
   
   The fix script now automatically fixes import paths in management commands.

3. **"Error storing in vector database: '_type'"**:
   These warnings are expected and safely handled by the system's error handling:
   - Content is still properly indexed in the database
   - Fallback embeddings are used when needed
   - System functionality is not impaired
   
   These warnings can be safely ignored.

4. **LLM Backend Not Available**:
   Ensure Ollama is running with:
   ```bash
   ollama serve
   ```
   
   Or check your OpenAI API key configuration in .env

8. Run the development server:
```bash
python manage.py runserver
```

## Demo Users

After running `python manage.py reset_db`, the following demo users are available:

### Admins
1. Admin User
   - Username: `admin`
   - Password: `admin123`
   - Email: admin@example.com
   - Full access to all features and settings

### Course Coordinators
1. Coordinator
   - Username: `coordinator`
   - Password: `coordinator123`
   - Email: coordinator@example.com
   - Can manage course assignments and enrollments

### Instructors
1. Dr. John Smith
   - Username: `dr.smith`
   - Password: `dr.smith123`
   - Email: dr.smith@example.com
   - Can create and manage courses

2. Dr. Sarah Johnson
   - Username: `dr.johnson`
   - Password: `dr.johnson123`
   - Email: dr.johnson@example.com
   - Can create and manage courses

3. Prof. Michael Williams
   - Username: `prof.williams`
   - Password: `prof.williams123`
   - Email: prof.williams@example.com
   - Can create and manage courses

### Students
1. John Doe
   - Username: `john.doe`
   - Password: `john.doe123`
   - Email: john@example.com
   - Can enroll in courses and take quizzes

2. Jane Smith
   - Username: `jane.smith`
   - Password: `jane.smith123`
   - Email: jane@example.com
   - Can enroll in courses and take quizzes

3. Bob Wilson
   - Username: `bob.wilson`
   - Password: `bob.wilson123`
   - Email: bob@example.com
   - Can enroll in courses and take quizzes

4. Alice Johnson
   - Username: `alice.johnson`
   - Password: `alice.johnson123`
   - Email: alice@example.com
   - Can enroll in courses and take quizzes

### Demo Scenarios

The seeded data includes several pre-configured scenarios that you can explore:

#### AI Tutor System
1. **Course-Specific AI Tutoring**
   - Log in as any student (e.g., john.doe)
   - Access a course detail page
   - Click on the "Get AI Tutor Help" button
   - Start a new conversation about the course content
   - Observe how the AI responds with course-specific knowledge
   - Try asking about other topics to see context-aware responses

2. **Module and Content Tutoring**
   - Log in as a student (e.g., jane.smith)
   - Navigate to a course learning page
   - Find the AI Tutor section in the sidebar
   - Select "Get help with this module" or "Get help with this content"
   - Ask specific questions about the current material
   - See how the AI provides contextual assistance

3. **Managing Tutor Sessions**
   - Log in as any user
   - Navigate to the AI Tutor sessions list (via main navigation)
   - View previous tutoring sessions
   - Create a new general session
   - Continue an existing conversation
   - Try different session types (course, module, content)

#### QR Code System
1. **Course QR Code Generation**
   - Log in as any user
   - Access a course detail page
   - Click on the "View QR Code" option in the sidebar
   - View and download the QR code for the course
   - View QR codes for individual modules

2. **QR Code Analytics**
   - Log in as Dr. Smith (Instructor) or Admin
   - Generate QR codes for a course
   - View scan statistics and analytics
   - Generate printable QR code sheets for distribution

3. **Mobile QR Code Scanning**
   - Log in on a mobile device
   - Use the built-in QR code scanner in the app
   - Scan a course or module QR code
   - Get redirected to the appropriate content

#### Admin System
1. **Activity Logging and Monitoring**
   - Log in as Admin (Administrator)
   - Access the Activity Log at `/dashboard/activity-log/`
   - Use filters to view specific activities:
     - Filter by date range
     - Filter by action type (login, course view, quiz attempt, etc.)
     - View detailed activity information including IP addresses and user agents
   - Monitor user engagement patterns
   - Track system usage trends

2. **System Health Dashboard**
   - Log in as Admin (Administrator)
   - Access the System Health dashboard at `/dashboard/system-health/`
   - View key metrics:
     - User statistics (total users, active users today)
     - Activity statistics (total activities, activities today)
     - Subscription statistics (active subscriptions, total revenue)
   - Monitor activity trends over the last 7 days
   - Check system component status (database, cache, file system, email)

3. **Enhanced User Management**
   - Log in as Admin (Administrator)
   - Access the Users dashboard at `/dashboard/users/`
   - View user activity statistics:
     - Total activities per user
     - Last activity timestamp
     - Activity type distribution
   - Monitor user engagement levels
   - Track user behavior patterns

#### Course Management
1. **Course Creation and Editing**
   - Log in as Dr. Smith (Instructor)
   - Create a new course or edit existing courses
   - Add modules and content
   - Create quizzes with different question types

2. **Course Coordination**
   - Log in as Coordinator (Course Coordinator)
   - Assign instructors to courses
   - Manage student enrollments
   - Review course analytics

#### Quiz System
1. **Quiz Creation and Management**
   - Log in as Dr. Johnson (Instructor)
   - Create quizzes with multiple question types
   - Set time limits and attempt limits
   - Preview quiz layout and functionality
   - Configure question randomization
   - Set up pre-check surveys

2. **Quiz Taking Experience**
   - Log in as John Doe (Student)
   - Take pre-configured quizzes
   - Experience time-limited quizzes with countdown timer
   - View per-question time tracking
   - See auto-submission on timeout
   - Review detailed quiz results with time spent per question

3. **Quiz Analytics Dashboard**
   - Log in as Prof. Williams (Instructor)
   - View comprehensive quiz statistics:
     - Overall attempt rates and completion times
     - Question-level performance metrics
     - Time tracking analytics (average, fastest, slowest times)
     - Timeout statistics
   - Analyze student performance patterns
   - Track question effectiveness
   - Monitor time usage patterns

#### Analytics and Reporting
1. **Instructor Analytics**
   - Log in as Dr. Smith (Instructor)
   - View student performance metrics
   - Analyze quiz results
   - Track course completion rates

2. **Coordinator Analytics**
   - Log in as Coordinator (Course Coordinator)
   - View course-wide statistics
   - Monitor instructor performance
   - Track enrollment trends

#### Student Experience
1. **Course Enrollment**
   - Log in as Jane Smith (Student)
   - Browse available courses
   - Enroll in courses
   - Track learning progress

2. **Quiz Attempts**
   - Log in as Bob Wilson (Student)
   - Take quizzes with different formats
   - View attempt history
   - Review performance analytics

#### Administrative Tasks
1. **User Management**
   - Log in as Admin (Administrator)
   - Access the system admin dashboard at `/dashboard/`
   - Use the Django admin interface at `/admin/` for detailed user management
   - Assign roles and permissions
   - View system-wide analytics

2. **System Configuration**
   - Log in as Admin (Administrator)
   - Access the system admin dashboard for high-level management
   - Use the Django admin interface for detailed system configuration
   - Manage course categories
   - Monitor system performance

3. **Admin Interfaces**
   - **System Admin Dashboard** (`/dashboard/`)
     - Overview of system statistics
     - Quick access to user management
     - Recent activity monitoring
     - Direct links to Django admin interface
   
   - **Django Admin Interface** (`/admin/`)
     - Detailed user management
     - Database-level operations
     - Advanced system configuration
     - Complete model management

Each scenario demonstrates different aspects of the system's functionality and can be explored without creating new records.

### Role-Based Access
The system uses Django's built-in groups and permissions system:

- **Administrator Group**
  - Full system access
  - All permissions granted
  - Can manage all users, courses, and system settings

- **Course Coordinator Group**
  - Can manage course assignments, enrollments, and instructor assignments
  - Has permissions to create, edit, and delete courses
  - Can manage course content and quizzes

- **Instructor Group**
  - Can create/edit courses, modules, and quizzes
  - Can view student progress and quiz results
  - Has permissions to manage their assigned courses

- **Student Group**
  - Can browse courses and enroll
  - Can take quizzes and track progress
  - Has basic view permissions for course content

Each group has specific Django permissions assigned to it, controlling access to different features and functionality throughout the system.

## Features

- Course Management
  - Course creation and editing
  - Module and content organization
  - File upload support
  - Course enrollment system
  - Course search and filtering
  - QR code generation for courses and modules

- User Management
  - User registration and authentication
  - Social authentication (Google)
  - User profiles and preferences
  - Role-based access control

- Content Management
  - Multiple content types (text, video, file, quiz, assignment)
  - File upload and management
  - Content organization
  - Version control

- Assessment System
  - Quiz creation with multiple question types
  - Pre-requisite surveys and knowledge checks
  - Assignment management
  - Grading system with detailed feedback
  - Progress tracking and scoring
  - Time limits and attempt tracking
  - Modern results display

- AI Tutor System
  - Interactive chat interface for personalized learning
  - Context-aware responses based on course content
  - Support for multiple LLM backends (Ollama, OpenAI)
  - Content indexing with RAG for relevant responses
  - Session management and conversation history
  - Course-specific and general tutoring options
  - Integration with course content and learning modules

- QR Code System
  - QR code generation for courses and modules
  - Printable QR code sheets
  - QR code analytics and tracking
  - Easy sharing and distribution

- UI/UX
  - Responsive design
  - Dark mode support
  - Accessibility features
  - Internationalization

## Project Structure

```
djangoapps/learnmore_plus/
├── apps/
│   ├── accounts/          # User management
│   ├── ai_tutor/          # AI Tutor functionality
│   ├── core/              # Core functionality
│   ├── courses/           # Course management
│   ├── dashboard/         # Admin dashboard
│   ├── qr_codes/          # QR code functionality
│   └── theme/             # Theming support
├── core/              # Core project functionality
├── docs/              # Project documentation
├── learnmore_plus/    # Project settings
├── templates/         # Base templates
├── static/            # Static files
├── media/             # User-uploaded files
├── requirements/      # Environment-specific requirements
│   ├── base.txt       # Base requirements
│   ├── dev.txt        # Development requirements
│   └── prod.txt       # Production requirements
└── staticfiles/       # Collected static files
```

## Configuration

1. Copy `.env.example` to `.env` and update the settings:
```bash
cp .env.example .env
```

2. Update the following settings in `.env`:
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

3. Optional: Configure AI Tutor settings in `.env`:
```
# For local development with Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# For production with OpenAI
OPENAI_API_KEY=your_api_key_here
DEFAULT_LLM_MODEL=gpt-3.5-turbo
```

After setting these variables, make sure to:
- Install Ollama from https://ollama.ai/ for local development
- Run the content indexing command: `python manage.py index_course_content`
- Seed demo data if needed: `python manage.py seed_ai_tutor_demo`

For more details, see the comprehensive documentation in `docs/ai-tutor-feature.md` and `docs/ai-tutor-demo.md`.

## Deployment

### Railway.app Deployment

This application is configured for easy deployment to Railway.app with two approaches:

#### Config-as-Code Approach (Recommended)

We've implemented Railway's Configuration as Code for simplified deployment:

1. **Configuration File**:
   - `railway.toml` - Defines all deployment settings, services, and dependencies

2. **Automated Features**:
   - Automatic database provisioning
   - Health checks and monitoring
   - Auto-scaling configuration
   - Automatic database migrations
   - Environment variable management

3. **Deployment Steps**:
   ```bash
   # Using Railway CLI with config-as-code
   railway login
   railway up
   ```

For details on this approach, see `docs/railway-config-as-code.md`.

#### Manual Approach

Alternatively, you can deploy using the traditional method:

1. **Required Files** (already included):
   - `Procfile` - Defines Railway application processes
   - `requirements.txt` - Consolidated dependencies
   - `runtime.txt` - Specifies Python version

2. **Production Settings**:
   - `learnmore_plus/settings/prod.py` is configured for Railway
   - Includes WhiteNoise for static file serving
   - Uses environment variables for configuration 
   - Configured to use `DATABASE_URL` provided by Railway

3. **Environment Variables to Set**:
   - `DJANGO_SETTINGS_MODULE=learnmore_plus.settings.prod`
   - `SECRET_KEY` (generate a new one for production)
   - `ALLOWED_HOSTS` (your Railway domain)
   - `OPENAI_API_KEY` (if using OpenAI for AI Tutor)

For complete deployment instructions, see `docs/railway-deployment.md`.

## Development

- Follow the development guidelines in `CONTRIBUTING.md`
- Keep documentation up to date
- Write tests for new features
- Follow the code style guide

## Testing

We have a comprehensive test suite for all key features of the application. Our testing strategy includes both backend unit/integration tests and end-to-end browser testing.

### Backend Testing

To run the backend tests:

```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run all tests with pytest (recommended)
pytest

# Run tests for specific apps
pytest apps/core/
pytest apps/ai_tutor/
pytest apps/qr_codes/

# Run with Django test runner
python manage.py test

# Run with coverage
coverage run -m pytest
coverage report
```

### End-to-End Testing with Playwright

We've implemented Playwright for automated browser testing to ensure the application works from a user's perspective. To run the E2E tests:

```bash
# Navigate to the e2e test directory
cd tests/e2e

# Install dependencies (first time only)
npm install
npx playwright install

# Run all tests
npx playwright test

# Run tests for a specific user type
npx playwright test student-demo.spec.js
npx playwright test instructor-demo.spec.js
npx playwright test admin-demo.spec.js

# Run tests in debug mode
npx playwright test --debug
```

For more information on our Playwright testing setup, see `docs/playwright-testing.md`.

### Key Test Areas

The test suite covers:

1. **UI Components**: Tests for our UI components in the flattened component structure (elements, sections)
2. **AI Tutor**: Tests for the AI tutoring system, including LLM factory, content indexing, and tutoring services
3. **QR Codes**: Tests for QR code generation, scanning, and statistics
4. **Template Syntax**: Tests to ensure proper template tag nesting and conditional logic
5. **Page Rendering**: Tests to ensure all key pages render without errors
6. **URL Configuration**: Tests for proper routing and URL pattern handling
7. **User Journeys**: End-to-end tests for different user types (admin, coordinator, instructor, student)

#### Template Syntax Testing

We have specific tests to catch template syntax issues that can break page rendering:

```bash
# Run the template syntax tests
./run_tests.sh core TemplateSyntaxErrorTests

# Manually check all templates for syntax issues
python check_templates.py
```

The template syntax tests specifically verify:
- Proper nesting of template tags (if/endif, with/endwith, etc.)
- Correct pattern usage for default values in components
- Proper indentation and spacing in templates
- Matching open/close tags for all control structures

For more information, see `docs/template-patterns.md` and `docs/template-fixes-summary.md`.

### Marking Tests

Tests can be marked with categories to organize and selectively run them:

```bash
# Run only unit tests
pytest -m unit

# Run only UI component tests
pytest -m ui

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Documentation

- `TODO.md` - Project task tracking
- `NOTES.md` - Implementation notes
- `CHECKPOINT.md` - Development checkpoints
- `CONTRIBUTING.md` - Contribution guidelines

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgments

- Django framework
- Tailwind CSS
- django-allauth
- Bootstrap Icons
- noUiSlider 

## Dashboard Roles & Access

### Platform Administrator (Super Admin)
- **Dashboard:** `/admin-dashboard/`
- **Purpose:** Onboard new users, manage all users and groups, view system-wide analytics and course performance summaries.
- **Access:** All users, all courses, all analytics.

### Course Coordinator
- **Dashboard:** `/courses/coordinator/dashboard/`
- **Purpose:** Manage a subset of courses, assign instructors, oversee enrollments, view analytics for coordinated courses.
- **Access:** Only courses they coordinate.

### Instructor
- **Dashboard:** `/courses/instructor/dashboard/`
- **Purpose:** Manage and teach their own courses, view analytics and student progress for their courses.
- **Access:** Only their assigned courses.

### Student
- **Dashboard:** `/courses/student/dashboard/`
- **Purpose:** View their own enrollments, progress, and achievements.
- **Access:** Only their own data.

### Routing & Permissions
- After login, users are redirected to the appropriate dashboard based on their group.
- Navigation and permissions are enforced so users only see dashboards and data relevant to their role.

### Note on Dashboards
- `/admin-dashboard/` is for platform-wide admin tasks and analytics (dashboard app).
- `/courses/admin/dashboard/` is for course-specific management (courses app).