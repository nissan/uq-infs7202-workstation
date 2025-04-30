# LearnMore Plus

A modern learning management system built with Django and Tailwind CSS.

## Features

- User authentication with social login
- Course catalog with search and filtering
- Course enrollment and progress tracking
- Module-based course content
- Learning interface with navigation
- Progress tracking and completion status

## Tech Stack

- Django 5.0
- Tailwind CSS
- PostgreSQL
- shadcn/ui components
- django-allauth for authentication

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Node.js (for Tailwind CSS)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/learnmore-plus.git
   cd learnmore-plus
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
learnmore_plus/
├── accounts/          # User authentication and profiles
├── courses/           # Course management
├── static/           # Static files
├── templates/        # HTML templates
└── learnmore_plus/   # Project settings
```

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django documentation
- Tailwind CSS
- shadcn/ui
- django-allauth 