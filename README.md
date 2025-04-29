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
  - Quiz creation
  - Assignment management
  - Grading system
  - Progress tracking

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