# Phase 1: Core Data & CRUD Checklist

This checklist covers the slice of work for migrating and validating the core data models and CRUD API.

## Models & Migrations
- [x] Verify `courses` and `progress` models match legacy requirements
- [ ] Run `makemigrations` and commit migrations for both apps

## Admin
- [x] Register `Course` and `Progress` in Django Admin

## API & Serializers
- [ ] Confirm `CourseSerializer` and `ProgressSerializer` define correct fields
- [ ] Test API endpoints for CourseViewSet (list, retrieve, create, update, destroy)
- [ ] Test API endpoints for ProgressViewSet (list, retrieve, create, update, destroy)

## Tests
- [ ] Write unit tests for serializers
- [ ] Write API tests for CRUD operations

## Docs
- [ ] Update README.md or reference this checklist