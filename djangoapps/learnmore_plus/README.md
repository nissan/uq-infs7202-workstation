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

6. Run the development server:
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

### Course Coordinators
1. Coordinator
   - Username: `coordinator`
   - Password: `coordinator123`
   - Email: coordinator@example.com

### Instructors
1. Dr. John Smith
   - Username: `dr.smith`
   - Password: `dr.smith123`
   - Email: dr.smith@example.com

2. Dr. Sarah Johnson
   - Username: `dr.johnson`
   - Password: `dr.johnson123`
   - Email: dr.johnson@example.com

3. Prof. Michael Williams
   - Username: `prof.williams`
   - Password: `prof.williams123`
   - Email: prof.williams@example.com

### Students
1. John Doe
   - Username: `john.doe`
   - Password: `john.doe123`
   - Email: john@example.com

2. Jane Smith
   - Username: `jane.smith`
   - Password: `jane.smith123`
   - Email: jane@example.com

3. Bob Wilson
   - Username: `bob.wilson`
   - Password: `bob.wilson123`
   - Email: bob@example.com

4. Alice Johnson
   - Username: `alice.johnson`
   - Password: `alice.johnson123`
   - Email: alice@example.com

### Demo Scenarios

The seeded data includes several pre-configured scenarios that you can explore:

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
   - Manage user accounts
   - Assign roles and permissions
   - View system-wide analytics

2. **System Configuration**
   - Log in as Admin (Administrator)
   - Configure system settings
   - Manage course categories
   - Monitor system performance

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
├── requirements/    # Environment-specific requirements
│   ├── base.txt    # Base requirements
│   ├── dev.txt     # Development requirements
│   └── prod.txt    # Production requirements
└── learnmore_plus/  # Project settings
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
- `/courses/admin/dashboard/`