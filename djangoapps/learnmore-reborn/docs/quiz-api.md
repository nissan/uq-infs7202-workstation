# Quiz System API Documentation

This document outlines the API endpoints available for interacting with the LearnMore quiz system.

## Base URL

All API endpoints are relative to the base URL: `/api/`

## Note on Concurrency

The quiz system includes protection against race conditions that may occur with concurrent operations, such as:
- Multiple simultaneous quiz attempt starts
- Concurrent answer submissions
- Simultaneous completion requests

While the SQLite database used in development has some limitations with concurrent operations, these protections are designed to work correctly in a production environment with a database like PostgreSQL that better handles concurrent transactions.

## Authentication

All endpoints require authentication using JWT. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Quizzes

### List Quizzes

Retrieves a list of quizzes available to the user.

- **URL**: `/quizzes/`
- **Method**: `GET`
- **URL Parameters**:
  - `module` (optional): Filter by module ID
  - `is_published` (optional): Filter by publication status (true/false)
  - `is_survey` (optional): Filter by quiz type (true/false)
  - `search` (optional): Search in title and description
- **Success Response**: 
  - **Code**: 200
  - **Content**: Array of quiz objects with basic information

### Get Quiz Details

Retrieves detailed information about a specific quiz.

- **URL**: `/quizzes/{id}/`
- **Method**: `GET`
- **URL Parameters**:
  - `id`: Quiz ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: Quiz object with questions
  - If user is an instructor, correct answers are included

### Create Quiz

Creates a new quiz. Only available to instructors.

- **URL**: `/quizzes/`
- **Method**: `POST`
- **Data Parameters**:
  - `module`: Module ID
  - `title`: Quiz title
  - `description`: Quiz description
  - `instructions`: Quiz instructions
  - `time_limit_minutes` (optional): Time limit
  - `passing_score`: Passing score percentage (0-100)
  - `randomize_questions` (optional): Whether to randomize question order
  - `allow_multiple_attempts` (optional): Whether multiple attempts are allowed
  - `max_attempts` (optional): Maximum attempts allowed
  - `is_published` (optional): Quiz publication status
  - `is_survey` (optional): Whether quiz is a survey
- **Success Response**: 
  - **Code**: 201
  - **Content**: Created quiz object

### Update Quiz

Updates an existing quiz. Only available to the quiz owner.

- **URL**: `/quizzes/{id}/`
- **Method**: `PUT`/`PATCH`
- **URL Parameters**:
  - `id`: Quiz ID
- **Data Parameters**: Same as Create Quiz
- **Success Response**: 
  - **Code**: 200
  - **Content**: Updated quiz object

### Delete Quiz

Deletes a quiz. Only available to the quiz owner.

- **URL**: `/quizzes/{id}/`
- **Method**: `DELETE`
- **URL Parameters**:
  - `id`: Quiz ID
- **Success Response**: 
  - **Code**: 204
  - **Content**: No content

### Start Quiz Attempt

Starts a new attempt for a quiz.

- **URL**: `/quizzes/{id}/start_attempt/`
- **Method**: `POST`
- **URL Parameters**:
  - `id`: Quiz ID
- **Success Response**: 
  - **Code**: 201
  - **Content**: QuizAttempt object
- **Error Responses**:
  - **Code**: 403
  - **Content**: `{"detail": "You must be enrolled in this course to take this quiz."}`
  - **Code**: 403
  - **Content**: `{"detail": "You have reached the maximum number of attempts for this quiz."}`

### List Quiz Attempts

Lists all attempts for a quiz by the current user.

- **URL**: `/quizzes/{id}/attempts/`
- **Method**: `GET`
- **URL Parameters**:
  - `id`: Quiz ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: Array of QuizAttempt objects

## Questions

### Multiple Choice Questions

#### List Multiple Choice Questions

Available only to instructors for their quizzes.

- **URL**: `/multiple-choice-questions/`
- **Method**: `GET`
- **Success Response**: 
  - **Code**: 200
  - **Content**: Array of multiple choice question objects

#### Create Multiple Choice Question

Creates a new multiple choice question. Only available to instructors.

- **URL**: `/multiple-choice-questions/`
- **Method**: `POST`
- **Data Parameters**:
  - `quiz`: Quiz ID
  - `text`: Question text
  - `points`: Points value
  - `order`: Question order
  - `allow_multiple`: Whether multiple answers are allowed
  - `explanation` (optional): Explanation for the answer
  - `correct_feedback` (optional): Feedback for correct answers
  - `incorrect_feedback` (optional): Feedback for incorrect answers
  - `choices`: Array of choice objects with:
    - `text`: Choice text
    - `is_correct`: Whether this choice is correct
    - `order`: Choice order
- **Success Response**: 
  - **Code**: 201
  - **Content**: Created question object with choices

### True/False Questions

#### List True/False Questions

Available only to instructors for their quizzes.

- **URL**: `/true-false-questions/`
- **Method**: `GET`
- **Success Response**: 
  - **Code**: 200
  - **Content**: Array of true/false question objects

#### Create True/False Question

Creates a new true/false question. Only available to instructors.

- **URL**: `/true-false-questions/`
- **Method**: `POST`
- **Data Parameters**:
  - `quiz`: Quiz ID
  - `text`: Question text
  - `points`: Points value
  - `order`: Question order
  - `correct_answer`: The correct answer (true/false)
  - `explanation` (optional): Explanation for the answer
  - `correct_feedback` (optional): Feedback for correct answers
  - `incorrect_feedback` (optional): Feedback for incorrect answers
- **Success Response**: 
  - **Code**: 201
  - **Content**: Created question object

## Quiz Attempts

### Get Quiz Attempt

Retrieves information about a specific quiz attempt.

- **URL**: `/quiz-attempts/{id}/`
- **Method**: `GET`
- **URL Parameters**:
  - `id`: Attempt ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: QuizAttempt object

### Submit Response

Submits an answer for a question in the current attempt.

- **URL**: `/quiz-attempts/{id}/submit_response/`
- **Method**: `POST`
- **URL Parameters**:
  - `id`: Attempt ID
- **Data Parameters**:
  - `question`: Question ID
  - `response_data`: JSON object with the answer data
    - For multiple choice single: `{"selected_choice": choice_id}`
    - For multiple choice multiple: `{"selected_choices": [choice_id1, choice_id2, ...]}`
    - For true/false: `{"selected_answer": true_or_false}`
  - `time_spent_seconds` (optional): Time spent on the question
- **Success Response**: 
  - **Code**: 200
  - **Content**: QuestionResponse object with grading results
- **Error Response**: 
  - **Code**: 400
  - **Content**: `{"detail": "This attempt has already been completed."}`

### Complete Quiz Attempt

Marks a quiz attempt as completed and calculates the final score.

- **URL**: `/quiz-attempts/{id}/complete/`
- **Method**: `POST`
- **URL Parameters**:
  - `id`: Attempt ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: Complete QuizAttempt object with score
- **Error Response**: 
  - **Code**: 400
  - **Content**: `{"detail": "This attempt has already been completed."}`

### Timeout Quiz Attempt

Marks a quiz attempt as timed out (when time limit is exceeded).

- **URL**: `/quiz-attempts/{id}/timeout/`
- **Method**: `POST`
- **URL Parameters**:
  - `id`: Attempt ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: QuizAttempt object with status="timed_out"
- **Error Response**: 
  - **Code**: 400
  - **Content**: `{"detail": "This attempt has already been completed."}`

### Abandon Quiz Attempt

Marks a quiz attempt as abandoned (when user quits early).

- **URL**: `/quiz-attempts/{id}/abandon/`
- **Method**: `POST`
- **URL Parameters**:
  - `id`: Attempt ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: QuizAttempt object with status="abandoned"
- **Error Response**: 
  - **Code**: 400
  - **Content**: `{"detail": "This attempt has already been completed."}`

### Get Quiz Attempt Result

Retrieves detailed results for a completed quiz attempt.

- **URL**: `/quiz-attempts/{id}/result/`
- **Method**: `GET`
- **URL Parameters**:
  - `id`: Attempt ID
- **Success Response**: 
  - **Code**: 200
  - **Content**: QuizAttempt object with detailed results, including all responses
- **Error Response**: 
  - **Code**: 400
  - **Content**: `{"detail": "This attempt has not been completed yet."}`