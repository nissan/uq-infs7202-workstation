# Phase 3: Course Catalog & Enrollment Checklist

This checklist covers migrating the course catalog and enrollment features into the `learnmore-reborn` app.

## Models & Migrations

- [x] Create `Enrollment` model in `courses/models.py` to track:
  - [x] User enrollment status
  - [x] Enrollment date
  - [x] Course access permissions
- [x] Add catalog-specific fields to `Course` model:
  - [x] Visibility status (public/private)
  - [x] Enrollment type (open/restricted)
  - [x] Maximum enrollment capacity
- [x] Run `makemigrations courses` and commit migrations

## Admin

- [x] Register `Enrollment` model in Django Admin
- [x] Add enrollment management interface
- [x] Add course catalog management features:
  - [x] Bulk visibility updates
  - [x] Enrollment capacity management
  - [x] Enrollment status overview

## API & Serializers

- [x] Create `EnrollmentSerializer` in `courses/serializers.py`
- [x] Update `CourseSerializer` with catalog-specific fields
- [x] Wire up DRF viewsets or APIViews for:
  - [x] `GET /api/courses/catalog/` (public course listing)
  - [x] `GET /api/courses/catalog/search/` (course search)
  - [x] `GET /api/courses/catalog/filter/` (course filtering)
  - [x] `POST /api/courses/{id}/enroll/` (enroll in course)
  - [x] `POST /api/courses/{id}/unenroll/` (unenroll from course)
  - [x] `GET /api/courses/enrolled/` (list enrolled courses)
- [x] Add URL patterns in `courses/api_urls.py`

## UI Components

- [x] Create course catalog page template
- [x] Implement course search component
- [x] Add course filtering interface
- [x] Create enrollment management UI
- [x] Add course enrollment status indicators
- [x] Implement responsive course cards

## Tests

- [ ] Write unit tests for:
  - [ ] Enrollment model
  - [ ] Course catalog serializers
  - [ ] Enrollment serializers
- [ ] Write API tests for:
  - [ ] Course catalog endpoints
  - [ ] Search and filter functionality
  - [ ] Enrollment operations
- [ ] Add UI component tests
- [ ] Test enrollment edge cases:
  - [ ] Maximum capacity reached
  - [ ] Restricted enrollment
  - [ ] Concurrent enrollment attempts

## Docs

- [x] Update `README.md` with course catalog and enrollment setup
- [x] Document API endpoints for catalog and enrollment
- [x] Add enrollment management guide
- [x] Document search and filter parameters 