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
For testing purposes, the following users are available:

#### Admin User
- Username: admin
- Password: admin123
- Role: Administrator

#### Instructors
- Username: instructor1
- Password: instructor123
- Role: Course Instructor

- Username: instructor2
- Password: instructor123
- Role: Course Instructor

#### Students
- Username: john
- Password: john123
- Role: Student

- Username: jane
- Password: jane123
- Role: Student

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