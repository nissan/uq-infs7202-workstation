# LearnMore Reborn - Django SaaS Learning Platform


This is the initial scaffold for the Enhanced LearnMore project, a Django-based SaaS learning platform with Django REST Framework (DRF) integration, `.env` configuration, and admin setup.

### ✅ Features Configured
- Django 4.x
- Django REST Framework
- django-environ for `.env` config
- django-cors-headers
- Virtual environment
- Basic app structure: `courses`, `progress`, `users`
- Initial `Course` and `Progress` models
- Admin user created
- `requirements.txt` frozen

---

## 📝 Setup Instructions

1. **Clone the repo & activate virtual environment:**

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
```

## Phase 1 Migration Checklist

Track the core data & CRUD migration tasks in [PHASE_1_CHECKLIST.md](PHASE_1_CHECKLIST.md).

Install dependencies:

```bash
pip install -r requirements.txt
```

Create .env file at project root:
```ini
DEBUG=True
SECRET_KEY=django-insecure-replace-this-with-a-better-key
ALLOWED_HOSTS=127.0.0.1,localhost
```

```bash
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run development server:

```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000/admin/

📂 Project Structure (key folders)
```bash
learnmore_reborn/
├── courses/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── progress/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── users/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── analytics/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── ai_tutor/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── learnmore/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
├── requirements.txt
├── manage.py
```