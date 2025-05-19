# Phase 1: Core Data & CRUD Checklist

This checklist covers the slice of work for migrating and validating the core data models and CRUD API.

## Models & Migrations
- [x] Verify `courses` and `progress` models match legacy requirements
- [x] Run `makemigrations` and commit migrations for both apps

## Admin
- [x] Register `Course` and `Progress` in Django Admin

## API & Serializers
- [x] Confirm `CourseSerializer` and `ProgressSerializer` define correct fields
- [x] Test API endpoints for CourseViewSet (list, retrieve, create, update, destroy)
- [x] Test API endpoints for ProgressViewSet (list, retrieve, create, update, destroy)

## Tests
- [x] Write unit tests for serializers
- [x] Write API tests for CRUD operations

## Docs
- [x] Update README.md or reference this checklist