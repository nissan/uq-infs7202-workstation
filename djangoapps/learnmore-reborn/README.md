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
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Create .env file at project root:

ini
Copy
Edit
DEBUG=True
SECRET_KEY=django-insecure-replace-this-with-a-better-key
ALLOWED_HOSTS=127.0.0.1,localhost
Run migrations:

bash
Copy
Edit
python manage.py migrate
Create superuser:

bash
Copy
Edit
python manage.py createsuperuser
Run development server:

bash
Copy
Edit
python manage.py runserver
Visit: http://127.0.0.1:8000/admin/

📂 Project Structure (key folders)
bash
Copy
Edit
enhanced_learnmore/
├── courses/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
├── progress/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
├── users/
├── enhanced_learnmore/
│   ├── settings.py
├── .env
├── requirements.txt
├── manage.py