# Google OAuth Implementation Guide

This document explains how the Google OAuth authentication has been implemented in LearnMore.

## Overview

Google OAuth has been integrated into the LearnMore application to allow users to sign in with their Google accounts. The implementation uses Django's `allauth` package, which provides a robust and secure way to handle social authentication.

## Configuration

### 1. Installed Apps

The following Django apps are required and have been added to `INSTALLED_APPS` in `settings.py`:

```python
'django.contrib.sites',
'allauth',
'allauth.account',
'allauth.socialaccount',
'allauth.socialaccount.providers.google',
```

### 2. Authentication Backends

The authentication backends have been configured in `settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

### 3. Social Account Providers

The Google provider is configured in `settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_OAUTH_CLIENT_ID', default=''),
            'secret': env('GOOGLE_OAUTH_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
```

### 4. Site ID

Django's sites framework is used by `allauth`. The site ID is set in `settings.py`:

```python
SITE_ID = 1
```

## URL Configuration

The following URLs are configured to handle OAuth authentication:

1. Main allauth URLs in `learnmore/urls.py`:
   ```python
   path('accounts/', include('allauth.urls')),
   path('accounts/google/login/', oauth2_login, name='google_login'),
   ```

2. Custom social login view in `users/urls.py`:
   ```python
   path('social-login/<str:provider>/', views.social_login_view, name='socialaccount_login'),
   ```

## UI Integration

The login page has a "Sign in with Google" button that redirects to the appropriate OAuth flow:

```html
<a href="{% url 'socialaccount_login' 'google' %}"
    class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
    <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
        <path fill="currentColor"
            d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
    </svg>
    Sign in with Google
</a>
```

## User Model Integration

The `UserProfile` model has a `google_id` field to store the Google user ID:

```python
google_id = models.CharField(max_length=100, blank=True, help_text="Google OAuth ID if user signs in with Google")
```

## API Integration

A `GoogleAuthView` API endpoint is available for frontend clients that need to authenticate with Google:

```python
path('api/users/google-auth/', GoogleAuthView.as_view(), name='google-auth'),
```

This endpoint accepts a POST request with:
- `google_id`: The Google user ID
- `email`: The user's email
- `first_name`: The user's first name
- `last_name`: The user's last name
- `profile_picture` (optional): URL to user's profile picture

## Setup Instructions

To use Google OAuth authentication, follow these steps:

1. Create Google OAuth credentials as described in `GOOGLE_OAUTH_SETUP.md`
2. Add the following to your `.env` file:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
   ```
3. Set up the proper redirect URIs in your Google Cloud Console
4. Ensure you've run migrations for the allauth models:
   ```
   python manage.py migrate
   ```
5. Configure the Site model in Django admin:
   - Go to Admin > Sites
   - Edit the default site or add a new one
   - Set Domain Name to your site's domain (e.g., `localhost:8000` for local development)
   - Set Display Name to your site's name (e.g., `LearnMore`)

## Troubleshooting

If you encounter issues with Google OAuth, check the following:

1. Verify your client ID and secret are correctly set in your `.env` file
2. Check that your redirect URIs are properly configured in Google Cloud Console
3. Ensure your site is properly configured in Django admin
4. Check the allauth logs for detailed error messages
5. Verify that you've set the correct scopes in your SOCIALACCOUNT_PROVIDERS settings

## Security Considerations

1. Never commit your OAuth credentials to version control
2. Use HTTPS in production to protect token exchanges
3. Regularly review your authorized applications in the Google Cloud Console
4. Set appropriate token timeouts and refresh mechanisms
5. Monitor authentication attempts for suspicious activity