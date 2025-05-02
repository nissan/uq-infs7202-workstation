# Enhanced LearnMore

A Django-based learning management system with AI-powered learning tools for educators and students worldwide.

## Features

- Course Management
  - Course creation and editing
  - Module and content organization
  - File upload support
  - Course enrollment system
  - Course search and filtering

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

- UI/UX
  - Responsive design
  - Dark mode support
  - Accessibility features
  - Internationalization

## Project Structure

```
djangoapps/learnmore_plus/
├── accounts/          # User management
├── core/             # Core functionality
├── courses/          # Course management
├── dashboard/        # Admin dashboard
├── templates/        # Base templates
├── static/          # Static files
└── learnmore_plus/  # Project settings
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/enhanced-learnmore.git
cd enhanced-learnmore
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
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

## Development

- Follow the development guidelines in `CONTRIBUTING.md`
- Keep documentation up to date
- Write tests for new features
- Follow the code style guide

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
- Coordinators and instructors have their own dashboards for their scope of courses.

## Overview
This LMS now features a fully API-driven seeder that creates a rich, realistic dataset for demoing all features, user roles, and workflows.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Reset and seed the database: `python manage.py reset_db`
3. Run the development server: `python manage.py runserver`
4. Log in as any demo user (see output after seeding)

## Showcase Script
To demo the system, use the following script as a guide:

1. **Admin**
   - Log in as Alice Morgan or Brian Lee
   - View/manage all users, courses, and system settings
2. **Coordinator**
   - Log in as Emily Brown or Michael Green
   - Manage course assignments, enrollments, and instructor assignments
   - View analytics and enrollment statuses
3. **Instructor**
   - Log in as John Smith, Sarah Johnson, Lisa White, or David Kim
   - Create/edit courses, modules, and quizzes
   - View student progress and quiz results
4. **Student**
   - Log in as any student (e.g., Jane Smith, Bob Wilson, etc.)
   - Browse and enroll in courses (pagination visible)
   - Complete modules, take quizzes (pre-check and knowledge-check)
   - View progress, quiz attempts, and course completion

## Demo Data
- 2 Admins, 2 Coordinators, 4 Instructors, 8+ Students
- 12+ Courses across multiple categories
- Each course has modules, content, quizzes, and enrollments
- All workflows and features are demo-ready

## TODO
- [ ] Continue to expand demo data as new features are added
- [ ] Add more advanced analytics and reporting
- [ ] Polish UI/UX for all dashboards 

## Recent UI/UX Improvements (2024-06)
- Improved button contrast and accessibility for homepage CTAs and 'Browse All Courses'.
- 'Browse All Courses' is now a prominent button, visible and accessible in both light and dark modes.
- Fixed number circle contrast in 'How Enhanced LearnMore Works'.
- Removed duplicate 'Or continue with' on login page.
- All changes follow accessibility and usability best practices.

### Quiz System
- **Comprehensive Quiz Management**
  - Multiple question types (multiple choice, true/false, short answer)
  - Time limits and auto-submission
  - Question randomization
  - Pre-check surveys
  - Prerequisite quizzes

- **Advanced Analytics**
  - Overview statistics (attempts, scores, pass rates)
  - Question-level performance metrics
  - Time tracking and analysis
  - Detailed attempt history
  - Modern, responsive dashboard

- **Time Tracking**
  - Real-time countdown timer
  - Per-question time tracking
  - Time limit enforcement
  - Auto-submission on timeout
  - Time statistics in analytics

### Course Management
- Course creation and management
- Module and content organization
- Student enrollment and progress tracking
- File uploads and management
- Rich text content editor

### User Management
- Role-based access control
- Student and instructor dashboards
- Progress tracking
- Course enrollment management

## Technical Stack
- Django 4.2
- Tailwind CSS
- PostgreSQL
- Redis (for caching)
- Celery (for background tasks)

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
We use Black for Python code formatting and ESLint for JavaScript:
```bash
# Format Python code
black .

# Format JavaScript code
npm run lint
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 