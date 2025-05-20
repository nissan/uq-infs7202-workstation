# Phase 2: User Auth & Profiles Checklist

This checklist covers migrating authentication and user profile features into the `learnmore-reborn` app.

## Models & Migrations

- [x] Decide on CustomUser vs default User model and update `AUTH_USER_MODEL` if needed
- [x] Implement UserProfile model in `users/models.py` (using default User model)
- [x] Run `makemigrations users` and commit migrations

## Admin

- [x] Register User and Profile models in `users/admin.py`

## API & Serializers

- [x] Create `RegistrationSerializer`, `LoginSerializer`, and `ProfileSerializer` in `users/serializers.py`
- [x] Wire up DRF viewsets or APIViews for:
  - [x] `POST /api/users/register/`
  - [x] `POST /api/users/login/`
  - [x] `POST /api/users/logout/`
  - [x] `GET/PUT /api/users/profile/`
  - [x] `POST /api/users/google-auth/` (Google OAuth integration)
- [x] Add URL patterns in `users/api_urls.py` and include them in root `learnmore/urls.py`

## Tests

- [x] Write unit tests for auth serializers and validators
- [x] Write API tests for registration, login, logout, and profile endpoints
- [x] Test Google OAuth integration

## Docs

- [x] Update `README.md` with setup instructions for authentication and profile management
- [x] Document API endpoints and authentication flows