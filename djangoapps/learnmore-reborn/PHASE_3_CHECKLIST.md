# Phase 3: Course Catalog & Enrollment Checklist

This checklist covers migrating the course catalog and enrollment features into the `learnmore-reborn` app.

## Models & Migrations

- [ ] Create `Enrollment` model in `courses/models.py` to track:
  - [ ] User enrollment status
  - [ ] Enrollment date
  - [ ] Course access permissions
- [ ] Add catalog-specific fields to `Course` model:
  - [ ] Visibility status (public/private)
  - [ ] Enrollment type (open/restricted)
  - [ ] Maximum enrollment capacity
- [ ] Run `makemigrations courses` and commit migrations

## Admin

- [ ] Register `Enrollment` model in Django Admin
- [ ] Add enrollment management interface
- [ ] Add course catalog management features:
  - [ ] Bulk visibility updates
  - [ ] Enrollment capacity management
  - [ ] Enrollment status overview

## API & Serializers

- [ ] Create `EnrollmentSerializer` in `courses/serializers.py`
- [ ] Update `CourseSerializer` with catalog-specific fields
- [ ] Wire up DRF viewsets or APIViews for:
  - [ ] `GET /api/courses/catalog/` (public course listing)
  - [ ] `GET /api/courses/catalog/search/` (course search)
  - [ ] `GET /api/courses/catalog/filter/` (course filtering)
  - [ ] `POST /api/courses/{id}/enroll/` (enroll in course)
  - [ ] `POST /api/courses/{id}/unenroll/` (unenroll from course)
  - [ ] `GET /api/courses/enrolled/` (list enrolled courses)
- [ ] Add URL patterns in `courses/api_urls.py`

## UI Components

- [ ] Create course catalog page template
- [ ] Implement course search component
- [ ] Add course filtering interface
- [ ] Create enrollment management UI
- [ ] Add course enrollment status indicators
- [ ] Implement responsive course cards

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

- [ ] Update `README.md` with course catalog and enrollment setup
- [ ] Document API endpoints for catalog and enrollment
- [ ] Add enrollment management guide
- [ ] Document search and filter parameters 