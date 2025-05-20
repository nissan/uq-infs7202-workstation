# Quiz System Documentation

This document provides an overview of the quiz system implemented in the LearnMore Reborn platform.

## Quiz System Overview

The quiz system allows instructors to create interactive assessments and surveys for course modules. It supports multiple question types, automatic grading, multiple attempts, and integration with the progress tracking system.

## Models

### Quiz Model

The `Quiz` model represents an assessment associated with a module. Key features include:

- Title, description, and instructions for the quiz
- Time limits and passing score requirements
- Multiple attempts settings with maximum attempt limits
- Published status and survey mode (surveys don't count toward grades)
- Question randomization option

### Question Models

The quiz system supports different question types through a base `Question` model with specialized subtypes:

- `MultipleChoiceQuestion`: Single or multiple correct answers with choices
- `TrueFalseQuestion`: Boolean true/false questions

All question types implement a `check_answer()` method that evaluates responses automatically.

### Quiz Attempt Models

Quiz attempts are tracked through:

- `QuizAttempt`: Records a user's session taking a quiz, including score and status
- `QuestionResponse`: Records a user's answer to each question and evaluates correctness

## API Endpoints

### Quiz Management

- `GET /api/courses/quizzes/`: List quizzes the user has access to
- `GET /api/courses/quizzes/{id}/`: Get quiz details with questions
- `POST /api/courses/quizzes/`: Create a new quiz (instructors only)
- `PUT/PATCH /api/courses/quizzes/{id}/`: Update a quiz (instructors only)
- `DELETE /api/courses/quizzes/{id}/`: Delete a quiz (instructors only)

### Question Management

- `POST /api/courses/multiple-choice-questions/`: Create a multiple-choice question
- `POST /api/courses/true-false-questions/`: Create a true/false question

### Quiz Taking

- `POST /api/courses/quizzes/{id}/start_attempt/`: Start a new quiz attempt
- `GET /api/courses/quizzes/{id}/attempts/`: Get user's attempts for a quiz
- `POST /api/courses/quiz-attempts/{id}/submit_response/`: Submit an answer to a question
- `POST /api/courses/quiz-attempts/{id}/complete/`: Complete a quiz attempt
- `POST /api/courses/quiz-attempts/{id}/timeout/`: Mark a quiz as timed out
- `POST /api/courses/quiz-attempts/{id}/abandon/`: Abandon a quiz attempt
- `GET /api/courses/quiz-attempts/{id}/result/`: Get detailed results for a completed attempt

## UI Elements

The quiz system provides several user interface templates:

- `quiz-list.html`: Lists all available quizzes for the user
- `quiz-detail.html`: Shows quiz details and previous attempts
- `quiz_assessment.html`: Interactive quiz-taking interface
- `quiz_results.html`: Displays detailed results after completing a quiz

## Integration with Progress Tracking

The quiz system integrates with the progress tracking system:

1. When a user passes a quiz (or completes a survey), the associated module is marked as completed
2. The module completion contributes to the overall course progress
3. Courses with quiz prerequisites enforce completion of quizzes before allowing access to dependent modules

## Auto-Grading Logic

Questions are automatically graded based on their type:

- **Multiple Choice (Single Answer)**: Correct if the selected choice matches the correct answer
- **Multiple Choice (Multiple Answers)**: Correct if all correct choices are selected and no incorrect choices are selected
- **True/False**: Correct if the selected Boolean value matches the correct answer

## Best Practices for Creating Quizzes

1. **Clear Instructions**: Provide clear instructions on how to complete the quiz
2. **Balanced Question Types**: Use a mix of question types to test different knowledge levels
3. **Appropriate Time Limits**: Set reasonable time limits based on question complexity
4. **Meaningful Feedback**: Add explanations for both correct and incorrect answers
5. **Multiple Attempts**: Consider allowing multiple attempts for practice quizzes
6. **Randomization**: Use question randomization for assessments to reduce cheating
7. **Progressive Difficulty**: Arrange questions from easier to more challenging
8. **Surveys vs. Assessments**: Use the survey flag for feedback collection that shouldn't affect progress

## Examples

### Creating a Quiz via API

```json
POST /api/courses/quizzes/
{
  "module": 1,
  "title": "Python Basics Quiz",
  "description": "Test your understanding of fundamental Python concepts",
  "instructions": "Answer all questions. You need 70% to pass.",
  "time_limit_minutes": 30,
  "passing_score": 70,
  "randomize_questions": true,
  "allow_multiple_attempts": true,
  "max_attempts": 3,
  "is_published": true,
  "is_survey": false
}
```

### Adding a Multiple Choice Question

```json
POST /api/courses/multiple-choice-questions/
{
  "quiz": 1,
  "text": "What is the correct way to create a function in Python?",
  "points": 1,
  "order": 1,
  "explanation": "Functions in Python are defined using the 'def' keyword, followed by the function name and parentheses.",
  "allow_multiple": false,
  "choices": [
    {
      "text": "function myFunc():",
      "is_correct": false,
      "order": 1
    },
    {
      "text": "def myFunc():",
      "is_correct": true,
      "order": 2
    },
    {
      "text": "create myFunc():",
      "is_correct": false,
      "order": 3
    },
    {
      "text": "new_function myFunc():",
      "is_correct": false,
      "order": 4
    }
  ]
}
```

### Submitting a Response

```json
POST /api/courses/quiz-attempts/5/submit_response/
{
  "question": 1,
  "response_data": {
    "selected_choice": 2
  },
  "time_spent_seconds": 45
}
```