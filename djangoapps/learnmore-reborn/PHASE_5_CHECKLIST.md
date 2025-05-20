# Phase 5: Quiz System - Basics Checklist

This checklist covers migrating the basic quiz system features into the `learnmore-reborn` app, focusing on multiple-choice and true/false questions with auto-grading.

## Models & Migrations

- [ ] Create `Quiz` model in `courses/models.py` with:
  - [ ] Title, description, instructions
  - [ ] Time limit (optional)
  - [ ] Passing score
  - [ ] Randomization settings
  - [ ] Relation to modules
- [ ] Create `Question` model as base class for:
  - [ ] Question text, order, points
  - [ ] Question type (MCQ, T/F)
  - [ ] Feedback for correct/incorrect answers
- [ ] Create `Choice` model for multiple-choice questions:
  - [ ] Choice text
  - [ ] Is correct flag
  - [ ] Feedback specific to this choice
- [ ] Create `QuizAttempt` model to track:
  - [ ] User information
  - [ ] Start and end times
  - [ ] Score and completion status
- [ ] Create `QuestionResponse` model to track:
  - [ ] Selected choices
  - [ ] Auto-grading results
  - [ ] Time spent on question
- [ ] Run `makemigrations courses` and commit migrations

## Admin

- [ ] Register quiz models in Django Admin
- [ ] Add quiz management interface with:
  - [ ] Inline formsets for questions and choices
  - [ ] Preview option for quizzes
  - [ ] Bulk question/choice operations
- [ ] Add attempt review interface for instructor feedback

## API & Serializers

- [ ] Create `QuizSerializer` in `courses/serializers.py`
- [ ] Create serializers for questions and choices
- [ ] Create `QuizAttemptSerializer` for tracking attempts
- [ ] Wire up DRF viewsets or APIViews for:
  - [ ] `GET /api/courses/quizzes/` (list all quizzes)
  - [ ] `GET /api/courses/quizzes/{id}/` (get quiz details with questions)
  - [ ] `POST /api/courses/quizzes/{id}/start/` (start a quiz attempt)
  - [ ] `POST /api/courses/quizzes/{id}/submit/` (submit answers)
  - [ ] `GET /api/courses/quizzes/{id}/result/` (get quiz results)
  - [ ] `GET /api/courses/quizzes/attempts/` (get quiz attempt history)
- [ ] Add URL patterns in `courses/api_urls.py`
- [ ] Connect quiz completion to module progress API

## UI Components

- [ ] Create quiz listing template
- [ ] Implement quiz assessment interface:
  - [ ] Timer for timed quizzes
  - [ ] Multiple-choice question display
  - [ ] True/False question display
  - [ ] Navigation between questions
  - [ ] Progress indicator for quiz
- [ ] Create quiz results and feedback page
- [ ] Add quiz attempt history view
- [ ] Implement quiz preview for instructors
- [ ] Add responsive design for mobile-friendly quizzes

## Auto-Grading Logic

- [ ] Implement auto-grading for MCQ questions
- [ ] Implement auto-grading for T/F questions
- [ ] Calculate scores and passing status
- [ ] Provide immediate feedback option
- [ ] Record granular question-level results

## Tests

- [ ] Write unit tests for:
  - [ ] Quiz and question models
  - [ ] Auto-grading logic
  - [ ] Quiz serializers
- [ ] Write API tests for:
  - [ ] Quiz listing and detail endpoints
  - [ ] Quiz attempt endpoints
  - [ ] Quiz result endpoints
- [ ] Add UI component tests
- [ ] Test quiz edge cases:
  - [ ] Time limit expiration
  - [ ] Partial completions
  - [ ] Multiple attempts
  - [ ] Instructor review

## Docs

- [ ] Update `README.md` with quiz system information
- [ ] Document API endpoints for quiz interaction
- [ ] Add quiz system implementation details
- [ ] Create quiz authoring guide for instructors

## Integration

- [ ] Connect quiz completion to module progress
- [ ] Link quiz results to user dashboard
- [ ] Add quiz analytics to course statistics
- [ ] Implement quiz availability based on module progress