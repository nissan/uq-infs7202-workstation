# Phase 5: Quiz System - Basics Checklist

This checklist covers implementing the basic quiz system with multiple-choice and true/false questions, along with auto-grading functionality in the `learnmore-reborn` app.

## Models & Migrations

- [ ] Enhance the existing `Quiz` model with additional fields:
  - [ ] `title`, `description`, `instructions` fields
  - [ ] `time_limit_minutes`, `passing_score` settings
  - [ ] `randomize_questions`, `allow_multiple_attempts`, `max_attempts` options
  - [ ] `is_published` status and `is_survey` flag
  - [ ] Add helper methods (`total_points()`, `passing_points()`)
- [ ] Create `Question` model as an abstract base class with:
  - [ ] Question text, type, order, points
  - [ ] Explanation and feedback fields
  - [ ] `check_answer()` abstract method
- [ ] Create `MultipleChoiceQuestion` model:
  - [ ] Implement `allow_multiple` flag for multiple answers
  - [ ] Override `check_answer()` for single/multiple answer scoring
- [ ] Create `TrueFalseQuestion` model:
  - [ ] Store `correct_answer` as boolean
  - [ ] Override `check_answer()` for true/false validation
- [ ] Create `Choice` model for answer options:
  - [ ] Link to multiple-choice questions
  - [ ] Store text, correctness, and order
  - [ ] Include feedback for each choice
- [ ] Create `QuizAttempt` model:
  - [ ] Track quiz session status and score
  - [ ] Store start/completion timestamps and duration
  - [ ] Implement `calculate_score()` and `mark_completed()` methods
  - [ ] Support multiple attempts with attempt numbering
- [ ] Create `QuestionResponse` model:
  - [ ] Store user's answers as JSON in `response_data`
  - [ ] Calculate correctness and points earned
  - [ ] Track time spent per question
  - [ ] Implement `check_answer()` to evaluate responses
- [ ] Run `makemigrations courses` and commit migrations

## Admin

- [ ] Register all quiz models in Django Admin
- [ ] Create `QuizAdmin` with:
  - [ ] List display with course, module, question count
  - [ ] Appropriate filters and search fields
  - [ ] Question inline for editing questions
- [ ] Create `MultipleChoiceQuestionAdmin` with:
  - [ ] Choice inline for editing options
  - [ ] Filter by course and quiz
- [ ] Create `TrueFalseQuestionAdmin`
- [ ] Create `QuizAttemptAdmin` with:
  - [ ] Read-only fields for attempt data
  - [ ] QuestionResponse inline for viewing responses
  - [ ] Score display with color coding
- [ ] Add quiz statistics to course/module admin dashboard

## API & Serializers

- [ ] Create serializers for choices:
  - [ ] `ChoiceSerializer` (without correct answer)
  - [ ] `ChoiceWithCorrectAnswerSerializer` (with correct answer)
- [ ] Create question serializers:
  - [ ] Base `QuestionSerializer`
  - [ ] `MultipleChoiceQuestionSerializer` with choices
  - [ ] `MultipleChoiceQuestionCreateSerializer` for creating questions with choices
  - [ ] `TrueFalseQuestionSerializer`
- [ ] Create quiz serializers:
  - [ ] `QuizListSerializer` with basic information
  - [ ] `QuizDetailSerializer` with questions and context-aware correct answers
- [ ] Create attempt serializers:
  - [ ] `QuestionResponseSerializer`
  - [ ] `QuizAttemptSerializer` with basic stats
  - [ ] `QuizAttemptDetailSerializer` with response details
- [ ] Wire up DRF viewsets:
  - [ ] `QuizViewSet` with permission handling
  - [ ] `MultipleChoiceQuestionViewSet` and `TrueFalseQuestionViewSet`
  - [ ] `QuizAttemptViewSet` for attempt management
- [ ] Implement custom actions:
  - [ ] `start_attempt` action for quiz
  - [ ] `attempts` action to list attempts
  - [ ] `submit_response` action for recording answers
  - [ ] `complete` action for finishing attempts
  - [ ] `result` action for viewing scores
- [ ] Add URL patterns in `courses/api_urls.py`

## UI Components

- [ ] Create quiz list template:
  - [ ] Implement filtering and search
  - [ ] Add responsive quiz cards
  - [ ] Show quiz metadata (time limit, passing score)
  - [ ] Display attempt history indicators
- [ ] Create quiz detail template:
  - [ ] Display quiz instructions and parameters
  - [ ] Show previous attempt summary
  - [ ] Add start quiz button with attempt limit check
  - [ ] List related quizzes in course
- [ ] Create quiz assessment interface:
  - [ ] Implement timer with auto-submit
  - [ ] Create question navigation and progress bar
  - [ ] Handle different question types (MCQ, T/F)
  - [ ] Add auto-save on navigation
  - [ ] Create finish and abandon quiz modals
- [ ] Create quiz results template:
  - [ ] Display overall score and pass/fail status
  - [ ] Show detailed question-level feedback
  - [ ] Include explanations and correct answers
  - [ ] Provide retake option when allowed
- [ ] Create quiz attempt history template:
  - [ ] List all attempts with stats
  - [ ] Show performance metrics
  - [ ] Provide access to detailed results

## Auto-Grading Logic

- [ ] Implement `check_answer()` in `MultipleChoiceQuestion`:
  - [ ] Handle single correct answer case
  - [ ] Handle multiple correct answers case
  - [ ] Return correctness, points, and feedback
- [ ] Implement `check_answer()` in `TrueFalseQuestion`:
  - [ ] Convert various input formats to boolean
  - [ ] Compare with correct answer
  - [ ] Return correctness, points, and feedback
- [ ] Implement `QuestionResponse.check_answer()`:
  - [ ] Dispatch to appropriate question type
  - [ ] Store results and feedback
- [ ] Implement `QuizAttempt.calculate_score()`:
  - [ ] Sum points from responses
  - [ ] Calculate percentage against maximum
  - [ ] Determine pass/fail status
- [ ] Connect quiz completion to module progress

## Tests

- [ ] Write model tests for:
  - [ ] Quiz and question models
  - [ ] Choice validation
  - [ ] Scoring algorithms for different question types
  - [ ] QuizAttempt and QuestionResponse functionality
- [ ] Write serializer tests for:
  - [ ] Correct handling of question types
  - [ ] Permission-based content filtering
  - [ ] Error handling for invalid inputs
- [ ] Write API tests for:
  - [ ] Quiz creation and management
  - [ ] Question creation with choices
  - [ ] Quiz attempt workflow
  - [ ] Response submission and auto-grading
  - [ ] Quiz completion and results calculation
- [ ] Test quiz edge cases:
  - [ ] Time limit expiration
  - [ ] Multiple correct answers
  - [ ] Randomized question order
  - [ ] Maximum attempt limits
  - [ ] Concurrent quiz attempts

## Docs

- [ ] Update `README.md` with quiz system setup
- [ ] Document API endpoints for quiz functionality
- [ ] Add quiz creation and management guide
- [ ] Document question types and scoring rules
- [ ] Create template patterns for quiz UI components

## Integration

- [ ] Connect quiz completion to module progress
- [ ] Update course navigation to include quiz links
- [ ] Add quiz analytics to learner statistics
- [ ] Implement quiz availability based on module prerequisites