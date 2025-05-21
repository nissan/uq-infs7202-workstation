# Deployment Guide for LearnMore Reborn

This document provides step-by-step instructions for deploying the LearnMore Reborn application to Railway.app. It covers environment setup, database configuration, and post-deployment tasks to ensure a functioning production environment.

## Prerequisites

- A [Railway.app](https://railway.app) account
- Git installed on your local machine
- A copy of this repository cloned locally

## Deployment Steps

### 1. Set Up Railway Project

1. Log in to [Railway.app](https://railway.app)
2. Create a new project from the Railway dashboard
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select the LearnMore Reborn repository

### 2. Configure Environment Variables

Configure the following environment variables in your Railway project settings:

```
DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=.railway.app
DATABASE_URL=${DATABASE_URL}
CSRF_TRUSTED_ORIGINS=https://*.railway.app
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=/app/media/
```

### 3. Add PostgreSQL Database

1. In your Railway project, click "New" to add a service
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set up the database and connect it to your project

### 4. Deploy the Application

1. Railway will automatically detect the Django application and start the deployment
2. Monitor the deployment logs for any issues
3. Once deployment is complete, click on the generated domain URL to access your application

### 5. Run Migrations and Create Superuser

After deployment, you need to run migrations and create an admin account. Use Railway's CLI or web terminal:

1. Install Railway CLI (if using CLI approach):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. Run migrations:
   ```bash
   railway run python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   railway run python manage.py createsuperuser
   ```
   - Enter the requested information (username, email, password)

### 6. Collect Static Files

Ensure static files are properly collected:

```bash
railway run python manage.py collectstatic --noinput
```

## Demo Account Setup

For ease of demonstration, create the following accounts:

### Admin Account
- Username: admin
- Email: admin@example.com
- Password: StrongAdminPass123!

### Instructor Account
- Username: instructor
- Email: instructor@example.com
- Password: StrongInstructorPass123!

### Student Account
- Username: student
- Email: student@example.com
- Password: StrongStudentPass123!

Create these accounts using:
```bash
railway run python manage.py shell -c "from users.models import CustomUser; CustomUser.objects.create_user(username='student', email='student@example.com', password='StrongStudentPass123!', is_instructor=False)"

railway run python manage.py shell -c "from users.models import CustomUser; CustomUser.objects.create_user(username='instructor', email='instructor@example.com', password='StrongInstructorPass123!', is_instructor=True)"
```

## Sample Data Generation

To populate the application with sample data:

```bash
railway run python manage.py shell -c "import create_test_data; create_test_data.create_sample_data()"
```

## Accessing the Deployed Application

- Main application: https://your-project-name.railway.app
- Admin interface: https://your-project-name.railway.app/admin

## Monitoring and Logs

- Railway provides built-in logs for each service
- Access logs from the Railway dashboard by selecting your service and clicking on the "Logs" tab

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify DATABASE_URL environment variable is correctly set
   - Check if PostgreSQL service is running

2. **Static Files Not Loading**
   - Ensure STATIC_URL and STATIC_ROOT are properly configured
   - Run collectstatic command again

3. **500 Internal Server Error**
   - Check application logs for detailed error messages
   - Verify all environment variables are correctly set
   - Ensure migrations have been applied

4. **CSRF Errors**
   - Verify CSRF_TRUSTED_ORIGINS includes your Railway domain

## Maintenance

### Database Backups

Railway automatically creates backups of your PostgreSQL database. To manually create a backup:

1. Go to your PostgreSQL service in Railway
2. Click on "Backups" tab
3. Click "Create Backup"

### Updating the Application

To update your deployed application after code changes:

1. Push changes to the connected GitHub repository
2. Railway will automatically detect changes and redeploy

## SSL/HTTPS

Railway provides SSL certificates automatically for all deployed applications. Your application will be accessible via HTTPS by default.

## Performance Considerations

- The free tier of Railway has limitations on usage and may sleep after periods of inactivity
- For production use, consider upgrading to a paid plan for better performance and reliability

## Conclusion

Your LearnMore Reborn application should now be successfully deployed to Railway. Use the admin account to access the admin interface and manage the application content.