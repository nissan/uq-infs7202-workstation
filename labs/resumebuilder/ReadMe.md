Here's a `README.md` tailored for your **Lab 6: Creating CRUD UIs** project:
# 💼 Lab 6 – Resume Builder: Creating CRUD UIs with Django

This repository contains the complete code for **Lab 6**. The goal of this lab is to create a fully functional **CRUD (Create, Read, Update, Delete) user interface** for managing resume data using Django class-based views, Bootstrap, and MySQL.

## 🚀 Features

- Create, edit, and delete subscribers (resume entries)
- Search and paginate through entries
- Success messages for user actions
- Clean UI using Bootstrap
- Built-in authentication support (can be extended in later labs)

---

## ⚙️ Setup Instructions

1. Within a virtual environment:

   ```bash
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Update your `settings.py`**:

   If you’re running on **UQ Cloud**, update the following values with your UQ Cloud Zone ID:

   ```python
   ALLOWED_HOSTS = ["your-zone-id.uqcloud.net", "infs3202-your-zone-id.uqcloud.net"]

   CSRF_TRUSTED_ORIGINS = [
       "https://your-zone-id.uqcloud.net",
       "https://infs3202-your-zone-id.uqcloud.net"
   ]
   ```

3. **Configure your database**:

   Make sure your `DATABASES` config in `settings.py` looks like this, and replace `yourpassword` with the correct MySQL root password:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'resumebuilder_db',
           'USER': 'root',
           'PASSWORD': 'yourpassword',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

4. **Run migrations and start the server**:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## 🔍 What You’ll Learn

- Building class-based views in Django
- Handling user feedback with Django messages
- Creating dynamic templates using Bootstrap
- Setting up MySQL with Django
- Deploying and testing in a cloud environment

---

Happy coding! 🎉
