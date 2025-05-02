# Enhanced LearnMore

A modern learning management system built with Django and Tailwind CSS.

## Features

### User Management
- Role-based access control
- User profiles with role assignments
- Course-specific permissions
- Secure authentication

### Course Management
- Course creation and organization
- Module and content management
- Quiz and assessment system
- Progress tracking

### Role-Based Features
- **Students**: Course access and learning
- **Instructors**: Course management and teaching
- **Course Coordinators**: Multi-course management
- **Administrators**: System-wide control

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/enhanced-learnmore.git
   cd enhanced-learnmore
   ```

2. Set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Set up roles and test data:
   ```bash
   python manage.py setup_roles
   python manage.py create_test_users
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```

## Test Users

The system includes pre-configured test users for each role:

### Admin
- Username: admin
- Password: admin123
- Full system access

### Course Coordinator
- Username: coordinator
- Password: coord123
- Can manage multiple courses

### Instructors
- Dr. John Smith (dr.smith/dr.smith123)
- Dr. Sarah Johnson (dr.johnson/dr.johnson123)
- Prof. Michael Williams (prof.williams/prof.williams123)

### Students
- John Doe (john.doe/john.doe123)
- Jane Smith (jane.smith/jane.smith123)
- Bob Wilson (bob.wilson/bob.wilson123)
- Alice Johnson (alice.johnson/alice.johnson123)

## Development

### Role-Based Development
1. Follow role-based access control patterns
2. Test features with different user roles
3. Document permission requirements
4. Maintain security best practices

### Testing
1. Test with different user roles
2. Verify course-specific permissions
3. Check access control boundaries
4. Validate user workflows

### Security
- Role-based access control
- Course-specific permissions
- Secure authentication
- Protected interfaces
- Permission validation

## Documentation
- [Development Notes](NOTES.md)
- [Getting Started](START.md)
- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Tech Stack

- Django 5.0
- Tailwind CSS
- PostgreSQL
- django-allauth for authentication
- shadcn/ui components (via CDN)

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