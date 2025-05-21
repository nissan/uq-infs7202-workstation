# Demo Accounts

This document explains how to set up and use the demo accounts for LearnMore Reborn LMS.

## Creating Demo Accounts

LearnMore Reborn includes management commands to quickly create demo accounts and content for testing and demonstration purposes.

### Option 1: Complete Demo Setup (Recommended)

For a complete demo environment with accounts, courses, and enrollments:

```bash
python manage.py setup_demo
```

This command:
1. Creates demo accounts (admin, instructor, student)
2. Creates sample courses and quizzes (if available)
3. Sets up enrollments for the demo student

### Option 2: Accounts Only

To create only the demo accounts without sample content:

```bash
python manage.py create_demo_accounts
```

This will create or update the demo accounts with consistent credentials.

### Demo Credentials

After running the command, the following accounts will be available:

#### Admin Account
- **Username:** demo_admin
- **Password:** demopass123
- **Email:** admin@example.com
- **Permissions:** Full admin access, can manage all aspects of the system

#### Instructor Account
- **Username:** demo_instructor
- **Password:** demopass123
- **Email:** instructor@example.com
- **Permissions:** Can create and manage courses, view analytics, grade assignments

#### Student Account
- **Username:** demo_student
- **Password:** demopass123
- **Email:** student@example.com
- **Permissions:** Can enroll in courses, take quizzes, view progress

## Security Notes

1. **Production Usage**: By default, the command will not run in production environments unless the `ALLOW_DEMO_ACCOUNTS` environment variable is set:
   ```bash
   DJANGO_ENV=production ALLOW_DEMO_ACCOUNTS=1 python manage.py create_demo_accounts
   ```

2. **Password Security**: These demo accounts use simple passwords for demonstration purposes. For any non-demo environment, you should:
   - Change these passwords immediately after creation
   - Set up proper authentication policies
   - Consider disabling these accounts when not needed

3. **Account Cleanup**: To remove demo accounts when they are no longer needed, you can use the Django admin interface or the shell:
   ```bash
   python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username__startswith='demo_').delete()"
   ```

## Customization

If you need to modify the demo accounts, edit the `create_demo_accounts.py` management command file located in:
```
users/management/commands/create_demo_accounts.py
```

The command is designed to be idempotent, meaning you can run it multiple times without creating duplicate accounts. It will update existing accounts if they already exist.