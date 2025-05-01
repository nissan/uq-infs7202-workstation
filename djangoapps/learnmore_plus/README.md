# LearnMore+ Learning Platform

A comprehensive learning management system built with Django and modern web technologies.

## Features

### Course Management
- Course catalog with filtering and search
- Course categories and levels
- Course enrollment system
- Progress tracking at course and module levels
- Time tracking for course completion
- Module-based content organization

### User Features
- User authentication and profiles
- Student dashboard with progress overview
- Detailed learning progress tracking
- Course enrollment management
- Module-level progress tracking
- Dark mode support
- Mobile-responsive design

### UI/UX Features
- Dark mode support with smooth transitions
- Mobile-first responsive design
- Enhanced button visibility
- Consistent hover states
- Improved text contrast
- Modern and clean interface

### Test Users
For testing purposes, the following users are automatically created during database migration:

#### Admin User
- Username: `admin`
- Password: `admin123`
- Email: admin@example.com
- Role: Superuser with full administrative access
- Features: Can access admin interface, manage all users, courses, and content

#### Instructors
1. Dr. Smith
   - Username: `dr.smith`
   - Password: `smith123`
   - Email: smith@example.com
   - Role: Course Instructor
   - Features: Can create and manage courses, view student progress

2. Dr. Johnson
   - Username: `dr.johnson`
   - Password: `johnson123`
   - Email: johnson@example.com
   - Role: Course Instructor
   - Features: Can create and manage courses, view student progress

3. General Instructor
   - Username: `instructor`
   - Password: `instructor123`
   - Email: instructor@example.com
   - Role: Course Instructor
   - Features: Can create and manage courses, view student progress

#### Students
1. John Doe
   - Username: `john`
   - Password: `john123`
   - Email: john@example.com
   - Role: Student
   - Features: Has sample enrollments in Python and Machine Learning courses
   - Progress: Various course progress records

2. Jane Smith
   - Username: `jane`
   - Password: `jane123`
   - Email: jane@example.com
   - Role: Student
   - Features: Has sample enrollments in Python, Machine Learning, and Data Structures courses
   - Progress: Various course progress records

Note: These test users are automatically created when you run `python manage.py migrate`. You can use these accounts to test different aspects of the system without creating new users.

## Getting Started

### Prerequisites
- Python 3.11+
- Django 5.2+
- PostgreSQL 15+

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nissan/uq-infs7202-workstation.git
   cd uq-infs7202-workstation/djangoapps/learnmore_plus
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

### Resetting the Database
If you need to reset the database to a clean state with fresh test data, follow these steps:

1. Clear all data from the database:
   ```bash
   python manage.py flush --no-input
   ```

2. Generate test data (courses, modules, content):
   ```bash
   python manage.py generate_test_data
   ```

3. Create test users:
   ```bash
   python manage.py create_test_users
   ```

This will give you a fresh database with:
- Sample courses and content
- Test users (admin, students, instructors)
- Course enrollments and progress data

### Testing Quiz Functionality
The test data includes quizzes in various courses. Here's how to test the quiz features:

1. Log in as a test student:
   - Username: `john`
   - Password: `john123`

2. Navigate to any course (they all have quizzes). For example, the "Complete Web Development Bootcamp" course has:
   - "Pre-Knowledge Check" in the "Course Introduction" module
   - "Core Concepts Quiz" in the "Core Concepts" module
   - "Final Assessment" in the "Advanced Topics" module

3. To take a quiz:
   - Go to the course page
   - Click on the module containing the quiz
   - Click on the quiz content item
   - Answer the questions (multiple choice, true/false, essay)
   - Submit your answers
   - View your score and correct answers

Quiz Features:
- Passing score: 70%
- Time limit: 30 minutes for pre-checks, 60 minutes for regular quizzes
- Attempts allowed: 3 for pre-checks, 2 for regular quizzes
- Questions are shuffled
- Correct answers are shown after submission

To test as an instructor:
- Username: `instructor`
- Password: `instructor123`

Instructors can:
- Create new quizzes
- Edit existing quizzes
- Add/remove questions
- View student attempts and scores

## Project Structure
```
learnmore_plus/
├── accounts/          # User account management
├── courses/           # Course management and learning
├── static/           # Static files
├── templates/        # HTML templates
└── manage.py         # Django management script
```

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Tech Stack

- Django 5.0
- Tailwind CSS
- PostgreSQL
- shadcn/ui components
- django-allauth for authentication

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
We use:
- Black for Python code formatting
- isort for import sorting
- flake8 for linting

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- Django documentation
- Tailwind CSS
- shadcn/ui
- django-allauth

## Documentation
- [START.md](START.md) - Getting started guide
- [TODO.md](TODO.md) - Project roadmap and tasks
- [CHECKPOINT.md](CHECKPOINT.md) - Project milestones
- [NOTES.md](NOTES.md) - Implementation notes 