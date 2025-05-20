# Phase 2: User Auth & Profiles Checklist

This checklist covers migrating authentication and user profile features into the `learnmore-reborn` app.

## Models & Migrations

- [ ] Decide on CustomUser vs default User model and update `AUTH_USER_MODEL` if needed
- [ ] Implement `CustomUser` model (if used) in `users/models.py`
- [ ] Run `makemigrations users` and commit migrations

## Admin

- [ ] Register `CustomUser` (or `User`) and `Profile` models in `users/admin.py`

## API & Serializers

- [ ] Create `RegistrationSerializer`, `LoginSerializer`, and `ProfileSerializer` in `users/serializers.py`
- [ ] Wire up DRF viewsets or APIViews for:
  - `POST /api/users/register/`
  - `POST /api/users/login/`
  - `POST /api/users/logout/`
  - `GET/PUT /api/users/profile/`
- [ ] Add URL patterns in `users/api_urls.py` and include them in root `learnmore/urls.py`

## Tests

- [ ] Write unit tests for auth serializers and validators
- [ ] Write API tests for registration, login, logout, and profile endpoints

## Docs

- [ ] Update `README.md` with setup instructions for authentication and profile management