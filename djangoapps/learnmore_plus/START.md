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
python manage.py seed_demo_data
```

8. Run the development server:
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

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue
4. Contact the development team
