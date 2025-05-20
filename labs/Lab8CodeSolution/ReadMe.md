# Lab 8 – Resume Builder: Creating and Using RESTFul API’s & Google Social Login

This repository contains the complete code for **Lab 8**. 

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
   Add your OpenAI API Key. 
   Add you Google Auth Client-ID and Secret

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


Happy coding! 🎉
