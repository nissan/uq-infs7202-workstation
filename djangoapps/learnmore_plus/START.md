# Getting Started with LearnMore Plus

This guide will help you set up the development environment for LearnMore Plus.

## Initial Setup

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

5. Create test users (optional):
   ```bash
   python manage.py createsuperuser  # Create admin user
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Test Users

The system comes with several pre-configured test users:

### Admin User
- Username: `admin`
- Password: `admin123`
- Role: Superuser with full access

### Instructors
- Username: `instructor1`
- Password: `instructor123`
- Role: Course instructor

- Username: `instructor2`
- Password: `instructor123`
- Role: Course instructor

### Students
- Username: `john`
- Password: `john123`
- Role: Test student

- Username: `jane`
- Password: `jane123`
- Role: Test student

## Project Structure

Set up the following directory structure:
```
learnmore_plus/
├── accounts/
│   ├── migrations/
│   ├── templates/
│   │   └── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── courses/
│   ├── migrations/
│   ├── templates/
│   │   └── courses/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   └── components/
├── learnmore_plus/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── .env
```

## Configuration

1. Update settings.py:
   - Add apps to INSTALLED_APPS
   - Configure database
   - Set up static files
   - Configure templates
   - Add authentication settings

2. Create .env file:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/learnmore
   ```

3. Set up Tailwind CSS:
   ```bash
   npm init -y
   npm install -D tailwindcss
   npx tailwindcss init
   ```

## Project Status and Next Steps

## Current Status (May 1, 2024)

### Completed Features
1. Core Course Management
   - Course creation and management
   - Module and content organization
   - Course catalog with filtering
   - Course enrollment system
   - Progress tracking
   - Time tracking

2. User Management
   - User authentication
   - Role-based access control
   - User profiles
   - Test user accounts

3. UI/UX Features
   - Dark mode support
   - Mobile responsiveness
   - Enhanced button visibility
   - Consistent hover states
   - Fixed text contrast issues

### Current Focus
- Course ratings and reviews
- Course completion certificates
- Additional test data
- Progress analytics enhancements

### Known Issues
1. None critical - all core features are working
2. Some UI improvements needed for mobile responsiveness
3. Need to add more comprehensive error handling

## Next Steps

### Immediate Tasks
1. Add course ratings and reviews system
2. Implement course completion certificates
3. Create more test data for courses
4. Enhance progress analytics

### Short-term Goals
1. Add course discussion forums
2. Implement advanced course search
3. Create instructor dashboard
4. Add course analytics

### Long-term Vision
1. Mobile app development
2. Real-time features
3. Advanced analytics
4. API development

## Development Guidelines

### Code Organization
- Follow Django best practices
- Use class-based views where appropriate
- Maintain consistent code style
- Document all major features

### Testing
- Write unit tests for new features
- Test edge cases
- Maintain test coverage
- Document test scenarios

### Documentation
- Keep README up to date
- Document API endpoints
- Maintain changelog
- Update user guides

## Getting Started for New Developers

1. Clone the repository
2. Set up development environment
3. Install dependencies
4. Run migrations
5. Create test user accounts
6. Start development server

## Resources

### Documentation
- Django documentation
- Project documentation
- API documentation
- User guides

### Tools
- Development environment setup
- Testing tools
- Deployment guides
- Monitoring tools

## Development Workflow

1. Create a new branch for each feature
2. Write tests before implementation
3. Follow PEP 8 style guide
4. Document changes
5. Create pull requests for review

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Troubleshooting

1. Database issues:
   - Check database connection settings
   - Verify migrations are applied
   - Check for conflicting migrations

2. Static files not loading:
   - Verify STATIC_URL and STATIC_ROOT settings
   - Run collectstatic
   - Check file permissions

3. Template issues:
   - Verify template directories in settings
   - Check template inheritance
   - Verify template tags

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [shadcn/ui Documentation](https://ui.shadcn.com/) 