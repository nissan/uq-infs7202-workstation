# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required for allauth
    
    # Local apps
    "accounts.apps.AccountsConfig",
    "core.apps.CoreConfig",
    "dashboard.apps.DashboardConfig",
    "courses.apps.CoursesConfig",
    
    # allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
] 