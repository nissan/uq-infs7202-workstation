# LearnMore Reborn API Documentation

This document provides comprehensive documentation for all API endpoints available in the LearnMore Reborn Learning Management System.

## Table of Contents

1. [Authentication](#authentication)
2. [Users & Profiles](#users--profiles)
3. [Courses & Enrollments](#courses--enrollments)
4. [Modules](#modules)
5. [Quiz System](#quiz-system)
6. [Progress Tracking](#progress-tracking)
7. [Analytics](#analytics)
8. [QR Codes](#qr-codes)

## Authentication

The LearnMore API uses JWT (JSON Web Tokens) for authentication. Most endpoints require an access token to be included in the request header.

### Authentication Flow

1. User registers or logs in
2. The server returns an access token and refresh token
3. Include the access token in all subsequent requests
4. When the access token expires, use the refresh token to get a new one

### Authentication Headers

```
Authorization: Bearer <access_token>
```

### Token Lifetimes

- Access tokens expire after 30 minutes
- Refresh tokens expire after 1 day

### Rate Limiting

The API implements rate limiting to prevent abuse:
- Anonymous users: 100 requests per day
- Authenticated users: 1000 requests per day
- Login attempts: 5 per minute

### Authentication Endpoints

#### Register User

```http
POST /api/users/register/
```

Create a new user account.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "password2": "string",
    "first_name": "string",
    "last_name": "string"
}
```

**Response (201 Created):**
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "profile": {
        "bio": "string",
        "student_id": "string",
        "department": "string",
        "is_instructor": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
}
```

#### Login

```http
POST /api/users/login/
```

Authenticate a user and receive JWT tokens.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response (200 OK):**
```json
{
    "refresh": "string",
    "access": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "profile": {
            "bio": "string",
            "student_id": "string",
            "department": "string",
            "is_instructor": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    }
}
```

#### Logout

```http
POST /api/users/logout/
```

Invalidate the refresh token.

**Request Body:**
```json
{
    "refresh": "string"
}
```

**Response (205 Reset Content):**
Empty response body

#### Refresh Token

```http
POST /api/users/token/refresh/
```

Get a new access token using a refresh token.

**Request Body:**
```json
{
    "refresh": "string"
}
```

**Response (200 OK):**
```json
{
    "access": "string"
}
```

#### Google Authentication

```http
POST /api/users/google-auth/
```

Authenticate or register a user using Google OAuth credentials.

**Request Body:**
```json
{
    "google_id": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "profile_picture": "string (optional)"
}
```

**Response (200 OK):**
```json
{
    "refresh": "string",
    "access": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "profile": {
            "bio": "string",
            "student_id": "string",
            "department": "string",
            "is_instructor": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    }
}
```

## Users & Profiles

### Profile Endpoints

#### Get User Profile

```http
GET /api/users/profile/
```

Get the current user's profile information.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
    "bio": "string",
    "student_id": "string",
    "department": "string",
    "is_instructor": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Update User Profile

```http
PUT /api/users/profile/
```

Update the current user's profile information.

**Authentication Required:** Yes

**Request Body:**
```json
{
    "bio": "string",
    "student_id": "string",
    "department": "string",
    "is_instructor": "boolean"
}
```

**Response (200 OK):**
```json
{
    "bio": "string",
    "student_id": "string",
    "department": "string",
    "is_instructor": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

## Courses & Enrollments

### Course Endpoints

#### List All Courses

```http
GET /api/courses/
```

Get a list of all courses (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 15,
    "next": "http://example.com/api/courses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Introduction to Programming",
            "slug": "introduction-to-programming",
            "description": "Learn the basics of programming",
            "status": "published",
            "enrollment_type": "open",
            "max_students": 50,
            "start_date": "2023-06-01",
            "end_date": "2023-09-01",
            "instructor": 2,
            "instructor_name": "John Smith",
            "created_at": "2023-05-15T10:30:00Z",
            "updated_at": "2023-05-20T14:20:00Z",
            "enrollment_count": 25,
            "is_full": false,
            "is_active": true
        },
        // More courses...
    ]
}
```

#### Get Course Details

```http
GET /api/courses/{id}/
```

Get details of a specific course.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Introduction to Programming",
    "slug": "introduction-to-programming",
    "description": "Learn the basics of programming",
    "status": "published",
    "enrollment_type": "open",
    "max_students": 50,
    "start_date": "2023-06-01",
    "end_date": "2023-09-01",
    "instructor": 2,
    "instructor_name": "John Smith",
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-20T14:20:00Z",
    "enrollment_count": 25,
    "is_full": false,
    "is_active": true,
    "modules": [
        {
            "id": 1,
            "title": "Getting Started",
            "description": "Introduction to the course",
            "order": 1
        }
        // More modules...
    ]
}
```

#### Create a Course

```http
POST /api/courses/
```

Create a new course (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "title": "string",
    "description": "string",
    "status": "draft|published|archived",
    "enrollment_type": "open|restricted",
    "max_students": 0,
    "start_date": "date",
    "end_date": "date",
    "course_type": "course|program|workshop|seminar"
}
```

**Response (201 Created):**
```json
{
    "id": 10,
    "title": "Introduction to AI",
    "slug": "introduction-to-ai",
    "description": "Learn the basics of artificial intelligence",
    "status": "draft",
    "enrollment_type": "open",
    "max_students": 0,
    "start_date": null,
    "end_date": null,
    "instructor": 2,
    "instructor_name": "John Smith",
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-15T10:30:00Z",
    "enrollment_count": 0,
    "is_full": false,
    "is_active": false
}
```

#### Update a Course

```http
PUT /api/courses/{id}/
```

Update an existing course (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "title": "string",
    "description": "string",
    "status": "draft|published|archived",
    "enrollment_type": "open|restricted",
    "max_students": 0,
    "start_date": "date",
    "end_date": "date",
    "course_type": "course|program|workshop|seminar"
}
```

**Response (200 OK):**
```json
{
    "id": 10,
    "title": "Advanced AI",
    "slug": "advanced-ai",
    "description": "Learn advanced concepts of artificial intelligence",
    "status": "published",
    "enrollment_type": "open",
    "max_students": 50,
    "start_date": "2023-06-01",
    "end_date": "2023-09-01",
    "instructor": 2,
    "instructor_name": "John Smith",
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-20T14:20:00Z",
    "enrollment_count": 0,
    "is_full": false,
    "is_active": true
}
```

#### Delete a Course

```http
DELETE /api/courses/{id}/
```

Delete a course (instructors only).

**Authentication Required:** Yes

**Response (204 No Content):**
Empty response body

### Course Catalog Endpoints

#### List Published Courses (Catalog)

```http
GET /api/courses/catalog/
```

Lists all published courses available for enrollment.

**Authentication Required:** No

**Query Parameters:**
- `enrollment_type`: Filter by enrollment type (options: "open", "restricted")
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 10,
    "next": "http://example.com/api/courses/catalog/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Introduction to Programming",
            "slug": "introduction-to-programming",
            "description": "Learn the basics of programming",
            "status": "published",
            "enrollment_type": "open",
            "max_students": 50,
            "start_date": "2023-06-01",
            "end_date": "2023-09-01",
            "instructor": 2,
            "instructor_name": "John Smith",
            "created_at": "2023-05-15T10:30:00Z",
            "updated_at": "2023-05-20T14:20:00Z",
            "enrollment_count": 25,
            "is_full": false,
            "is_active": true
        },
        // More courses...
    ]
}
```

#### Search Courses

```http
GET /api/courses/catalog/search/
```

Search for courses by title or description.

**Authentication Required:** No

**Query Parameters:**
- `q`: Search query string (required)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
Same format as the catalog endpoint

### Enrollment Endpoints

#### Enroll in Course

```http
POST /api/courses/{slug}/enroll/
```

Enrolls the authenticated user in a specific course.

**Authentication Required:** Yes

**URL Parameters:**
- `slug`: Course slug to enroll in

**Response (201 Created):**
```json
{
    "id": 25,
    "user": 5,
    "user_username": "student1",
    "course": 1,
    "course_title": "Introduction to Programming",
    "status": "active",
    "progress": 0,
    "enrolled_at": "2023-06-01T08:45:00Z",
    "completed_at": null
}
```

#### Unenroll from Course

```http
POST /api/courses/{slug}/unenroll/
```

Unenrolls the authenticated user from a specific course.

**Authentication Required:** Yes

**URL Parameters:**
- `slug`: Course slug to unenroll from

**Response (204 No Content):**
Empty response body

#### List Enrolled Courses

```http
GET /api/courses/enrolled/
```

Lists all courses the authenticated user is actively enrolled in.

**Authentication Required:** Yes

**Response (200 OK):**
```json
[
    {
        "id": 25,
        "user": 5,
        "user_username": "student1",
        "course": 1,
        "course_title": "Introduction to Programming",
        "status": "active",
        "progress": 15,
        "enrolled_at": "2023-06-01T08:45:00Z",
        "completed_at": null
    },
    // More enrollments...
]
```

#### List All Enrollments

```http
GET /api/enrollments/
```

Lists all enrollments (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `user`: Filter by user ID
- `status`: Filter by status (active, completed, dropped)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "http://example.com/api/enrollments/?page=2",
    "previous": null,
    "results": [
        {
            "id": 25,
            "user": 5,
            "user_username": "student1",
            "course": 1,
            "course_title": "Introduction to Programming",
            "status": "active",
            "progress": 15,
            "enrolled_at": "2023-06-01T08:45:00Z",
            "completed_at": null
        },
        // More enrollments...
    ]
}
```

## Modules

### Module Endpoints

#### List Modules

```http
GET /api/modules/
```

List all modules the user has access to.

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://example.com/api/modules/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "course": 1,
            "course_title": "Introduction to Programming",
            "title": "Getting Started",
            "description": "Introduction to the course",
            "order": 1,
            "completion_criteria": "quiz",
            "content": "# Welcome to the Course\n\nThis module introduces you to the basics...",
            "is_published": true,
            "created_at": "2023-05-15T10:30:00Z",
            "updated_at": "2023-05-20T14:20:00Z"
        },
        // More modules...
    ]
}
```

#### Get Module Details

```http
GET /api/modules/{id}/
```

Get details of a specific module.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
    "id": 1,
    "course": 1,
    "course_title": "Introduction to Programming",
    "title": "Getting Started",
    "description": "Introduction to the course",
    "order": 1,
    "completion_criteria": "quiz",
    "content": "# Welcome to the Course\n\nThis module introduces you to the basics...",
    "is_published": true,
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-20T14:20:00Z",
    "quizzes": [
        {
            "id": 1,
            "title": "Module 1 Quiz",
            "description": "Test your understanding of the basics",
            "time_limit_minutes": 30,
            "passing_score": 70
        }
    ]
}
```

#### Create a Module

```http
POST /api/modules/
```

Create a new module (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "course": 1,
    "title": "string",
    "description": "string",
    "order": 1,
    "completion_criteria": "quiz|content|hybrid",
    "content": "string (markdown)",
    "is_published": false
}
```

**Response (201 Created):**
```json
{
    "id": 5,
    "course": 1,
    "course_title": "Introduction to Programming",
    "title": "Advanced Topics",
    "description": "Advanced programming concepts",
    "order": 4,
    "completion_criteria": "hybrid",
    "content": "# Advanced Topics\n\nIn this module, we'll explore...",
    "is_published": false,
    "created_at": "2023-06-01T08:45:00Z",
    "updated_at": "2023-06-01T08:45:00Z"
}
```

#### Update a Module

```http
PUT /api/modules/{id}/
```

Update an existing module (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "course": 1,
    "title": "string",
    "description": "string",
    "order": 1,
    "completion_criteria": "quiz|content|hybrid",
    "content": "string (markdown)",
    "is_published": false
}
```

**Response (200 OK):**
```json
{
    "id": 5,
    "course": 1,
    "course_title": "Introduction to Programming",
    "title": "Expert Topics",
    "description": "Expert programming concepts",
    "order": 5,
    "completion_criteria": "hybrid",
    "content": "# Expert Topics\n\nIn this module, we'll dive deep into...",
    "is_published": true,
    "created_at": "2023-06-01T08:45:00Z",
    "updated_at": "2023-06-05T10:15:00Z"
}
```

#### Delete a Module

```http
DELETE /api/modules/{id}/
```

Delete a module (instructors only).

**Authentication Required:** Yes

**Response (204 No Content):**
Empty response body

## Quiz System

### Quiz Endpoints

#### List Quizzes

```http
GET /api/quizzes/
```

List all quizzes the user has access to.

**Authentication Required:** Yes

**Query Parameters:**
- `module`: Filter by module ID
- `is_published`: Filter by published status (true/false)
- `is_survey`: Filter by survey status (true/false)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 15,
    "next": "http://example.com/api/quizzes/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
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
            "is_survey": false,
            "created_at": "2023-05-15T10:30:00Z",
            "updated_at": "2023-05-20T14:20:00Z"
        },
        // More quizzes...
    ]
}
```

#### Get Quiz Details

```http
GET /api/quizzes/{id}/
```

Get details of a specific quiz.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
    "id": 1,
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
    "is_survey": false,
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-20T14:20:00Z",
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "text": "What is the correct way to create a function in Python?",
            "points": 1,
            "choices": [
                {
                    "id": 1,
                    "text": "function myFunc():",
                    "is_correct": false
                },
                {
                    "id": 2,
                    "text": "def myFunc():",
                    "is_correct": true
                },
                // More choices...
            ]
        },
        // More questions...
    ]
}
```

#### Create a Quiz

```http
POST /api/quizzes/
```

Create a new quiz (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "module": 1,
    "title": "string",
    "description": "string",
    "instructions": "string",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "randomize_questions": true,
    "allow_multiple_attempts": true,
    "max_attempts": 3,
    "is_published": false,
    "is_survey": false,
    "access_code": "string (optional)",
    "allow_time_extension": false
}
```

**Response (201 Created):**
```json
{
    "id": 5,
    "module": 1,
    "title": "Advanced Python Quiz",
    "description": "Test your understanding of advanced Python concepts",
    "instructions": "Answer all questions. You need 80% to pass.",
    "time_limit_minutes": 45,
    "passing_score": 80,
    "randomize_questions": true,
    "allow_multiple_attempts": true,
    "max_attempts": 2,
    "is_published": false,
    "is_survey": false,
    "created_at": "2023-06-01T08:45:00Z",
    "updated_at": "2023-06-01T08:45:00Z"
}
```

#### Update a Quiz

```http
PUT /api/quizzes/{id}/
```

Update an existing quiz (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "module": 1,
    "title": "string",
    "description": "string",
    "instructions": "string",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "randomize_questions": true,
    "allow_multiple_attempts": true,
    "max_attempts": 3,
    "is_published": false,
    "is_survey": false,
    "access_code": "string (optional)",
    "allow_time_extension": false
}
```

**Response (200 OK):**
```json
{
    "id": 5,
    "module": 1,
    "title": "Expert Python Quiz",
    "description": "Test your understanding of expert Python concepts",
    "instructions": "Answer all questions. You need 90% to pass.",
    "time_limit_minutes": 60,
    "passing_score": 90,
    "randomize_questions": true,
    "allow_multiple_attempts": true,
    "max_attempts": 1,
    "is_published": true,
    "is_survey": false,
    "created_at": "2023-06-01T08:45:00Z",
    "updated_at": "2023-06-05T10:15:00Z"
}
```

#### Delete a Quiz

```http
DELETE /api/quizzes/{id}/
```

Delete a quiz (instructors only).

**Authentication Required:** Yes

**Response (204 No Content):**
Empty response body

### Quiz Taking Endpoints

#### Start Quiz Attempt

```http
POST /api/courses/quizzes/{id}/start-attempt/
```

Start a new attempt for a quiz.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz ID

**Request Body:**
```json
{
    "access_code": "string (optional)"
}
```

**Response (201 Created):**
```json
{
    "id": 10,
    "quiz": 1,
    "quiz_title": "Python Basics Quiz",
    "user": 5,
    "started_at": "2023-06-10T14:30:00Z",
    "completed_at": null,
    "score": null,
    "status": "in_progress",
    "time_remaining_seconds": 1800,
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "text": "What is the correct way to create a function in Python?",
            "choices": [
                {
                    "id": 1,
                    "text": "function myFunc():"
                },
                {
                    "id": 2,
                    "text": "def myFunc():"
                },
                // More choices...
            ]
        },
        // More questions...
    ]
}
```

#### Submit Question Response

```http
POST /api/courses/quiz-attempts/{id}/submit-response/
```

Submit an answer to a question during a quiz attempt.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz attempt ID

**Request Body:**
```json
{
    "question": 1,
    "response_data": {
        "selected_choice": 2
    },
    "time_spent_seconds": 45
}
```

**Response (200 OK):**
```json
{
    "id": 15,
    "quiz_attempt": 10,
    "question": 1,
    "question_text": "What is the correct way to create a function in Python?",
    "response_data": {
        "selected_choice": 2
    },
    "is_correct": true,
    "score": 1,
    "time_spent_seconds": 45,
    "submitted_at": "2023-06-10T14:31:00Z"
}
```

#### Complete Quiz Attempt

```http
POST /api/courses/quiz-attempts/{id}/complete/
```

Complete a quiz attempt.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz attempt ID

**Response (200 OK):**
```json
{
    "id": 10,
    "quiz": 1,
    "quiz_title": "Python Basics Quiz",
    "user": 5,
    "started_at": "2023-06-10T14:30:00Z",
    "completed_at": "2023-06-10T14:45:00Z",
    "score": 85,
    "status": "completed",
    "passed": true,
    "time_spent_seconds": 900
}
```

#### Timeout Quiz Attempt

```http
POST /api/courses/quiz-attempts/{id}/timeout/
```

Mark a quiz attempt as timed out.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz attempt ID

**Response (200 OK):**
```json
{
    "id": 10,
    "quiz": 1,
    "quiz_title": "Python Basics Quiz",
    "user": 5,
    "started_at": "2023-06-10T14:30:00Z",
    "completed_at": "2023-06-10T15:00:00Z",
    "score": 50,
    "status": "timed_out",
    "passed": false,
    "time_spent_seconds": 1800
}
```

#### Abandon Quiz Attempt

```http
POST /api/courses/quiz-attempts/{id}/abandon/
```

Abandon a quiz attempt.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz attempt ID

**Response (200 OK):**
```json
{
    "id": 10,
    "quiz": 1,
    "quiz_title": "Python Basics Quiz",
    "user": 5,
    "started_at": "2023-06-10T14:30:00Z",
    "completed_at": "2023-06-10T14:40:00Z",
    "score": null,
    "status": "abandoned",
    "passed": false,
    "time_spent_seconds": 600
}
```

#### Get Quiz Result

```http
GET /api/courses/quiz-attempts/{id}/result/
```

Get detailed results for a completed quiz attempt.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz attempt ID

**Response (200 OK):**
```json
{
    "id": 10,
    "quiz": 1,
    "quiz_title": "Python Basics Quiz",
    "user": 5,
    "started_at": "2023-06-10T14:30:00Z",
    "completed_at": "2023-06-10T14:45:00Z",
    "score": 85,
    "status": "completed",
    "passed": true,
    "time_spent_seconds": 900,
    "responses": [
        {
            "id": 15,
            "question": 1,
            "question_text": "What is the correct way to create a function in Python?",
            "question_type": "multiple_choice",
            "response_data": {
                "selected_choice": 2
            },
            "is_correct": true,
            "score": 1,
            "feedback": "Correct! In Python, functions are defined using the 'def' keyword.",
            "time_spent_seconds": 45
        },
        // More responses...
    ]
}
```

#### Grant Time Extension

```http
POST /api/courses/quiz-attempts/{id}/grant-extension/
```

Grant a time extension for a quiz attempt (instructors only).

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz attempt ID

**Request Body:**
```json
{
    "additional_minutes": 15
}
```

**Response (200 OK):**
```json
{
    "id": 10,
    "quiz": 1,
    "quiz_title": "Python Basics Quiz",
    "user": 5,
    "started_at": "2023-06-10T14:30:00Z",
    "completed_at": null,
    "score": null,
    "status": "in_progress",
    "time_remaining_seconds": 2700,
    "extended_minutes": 15
}
```

### Essay Question Endpoints

#### Grade Essay Response

```http
POST /api/courses/question-responses/{id}/grade-essay/
```

Grade an essay question response (instructors only).

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Question response ID

**Request Body:**
```json
{
    "score": 8,
    "feedback": "Good analysis, but could use more supporting evidence.",
    "rubric_scores": {
        "content": 3,
        "organization": 2,
        "grammar": 3
    }
}
```

**Response (200 OK):**
```json
{
    "id": 20,
    "quiz_attempt": 10,
    "question": 5,
    "question_text": "Explain the concept of inheritance in object-oriented programming.",
    "response_data": {
        "essay_text": "Inheritance is a key concept in OOP that allows..."
    },
    "is_graded": true,
    "score": 8,
    "max_score": 10,
    "feedback": "Good analysis, but could use more supporting evidence.",
    "graded_at": "2023-06-12T10:15:00Z",
    "graded_by": "instructor1",
    "rubric_scores": {
        "content": 3,
        "organization": 2,
        "grammar": 3
    }
}
```

#### List Pending Essay Grading

```http
GET /api/courses/question-responses/pending-grading/
```

Get a list of essay responses that need grading (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `quiz`: Filter by quiz ID
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 20,
            "quiz_attempt": 10,
            "student_name": "John Doe",
            "quiz_title": "Advanced Concepts Quiz",
            "question": 5,
            "question_text": "Explain the concept of inheritance in object-oriented programming.",
            "response_data": {
                "essay_text": "Inheritance is a key concept in OOP that allows..."
            },
            "is_graded": false,
            "submitted_at": "2023-06-10T15:30:00Z"
        },
        // More responses...
    ]
}
```

### Quiz Analytics Endpoints

#### Get Quiz Analytics

```http
GET /api/courses/quizzes/{id}/analytics/
```

Get analytics data for a quiz (instructors only).

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz ID

**Response (200 OK):**
```json
{
    "quiz_id": 1,
    "quiz_title": "Python Basics Quiz",
    "attempt_count": 25,
    "completion_rate": 92,
    "average_score": 78.5,
    "pass_rate": 85,
    "average_time_spent_minutes": 22.3,
    "question_performance": [
        {
            "question_id": 1,
            "question_text": "What is the correct way to create a function in Python?",
            "correct_response_rate": 95,
            "average_score": 0.95,
            "average_time_spent_seconds": 35
        },
        // More questions...
    ]
}
```

#### Recalculate Quiz Analytics

```http
POST /api/courses/quizzes/{id}/recalculate-analytics/
```

Recalculate analytics data for a quiz (instructors only).

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Quiz ID

**Response (200 OK):**
```json
{
    "status": "success",
    "message": "Quiz analytics recalculated successfully",
    "last_calculated": "2023-06-12T14:30:00Z"
}
```

## Progress Tracking

### Progress Endpoints

#### Get User Progress

```http
GET /api/progress/
```

Get the current user's progress across all enrolled courses.

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 10,
            "course": 1,
            "course_title": "Introduction to Programming",
            "user": 5,
            "percentage_complete": 35,
            "modules_completed": 2,
            "total_modules": 6,
            "quizzes_completed": 2,
            "total_quizzes": 4,
            "last_activity": "2023-06-10T15:30:00Z",
            "completion_date": null
        },
        // More courses...
    ]
}
```

#### Get Module Progress

```http
GET /api/module-progress/
```

Get the current user's progress across all modules.

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `module`: Filter by module ID
- `status`: Filter by status (not_started, in_progress, completed)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 25,
            "module": 1,
            "module_title": "Getting Started",
            "course": 1,
            "course_title": "Introduction to Programming",
            "user": 5,
            "status": "completed",
            "started_at": "2023-06-05T10:30:00Z",
            "completed_at": "2023-06-05T11:45:00Z",
            "time_spent_minutes": 75,
            "last_activity": "2023-06-05T11:45:00Z"
        },
        // More modules...
    ]
}
```

#### Reset Module Progress

```http
POST /api/module-progress/{id}/reset/
```

Reset progress for a specific module.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Module progress ID

**Response (200 OK):**
```json
{
    "id": 25,
    "module": 1,
    "module_title": "Getting Started",
    "course": 1,
    "course_title": "Introduction to Programming",
    "user": 5,
    "status": "not_started",
    "started_at": null,
    "completed_at": null,
    "time_spent_minutes": 0,
    "last_activity": "2023-06-12T09:30:00Z",
    "reset_at": "2023-06-12T09:30:00Z"
}
```

## Analytics

### User Activity Endpoints

#### Get User Activity

```http
GET /api/analytics/user-activity/
```

Get activity data for the current user.

**Authentication Required:** Yes

**Query Parameters:**
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://example.com/api/analytics/user-activity/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": 5,
            "activity_type": "module_view",
            "target_id": 1,
            "target_name": "Getting Started",
            "course_id": 1,
            "course_title": "Introduction to Programming",
            "occurred_at": "2023-06-10T10:30:00Z",
            "session_duration_minutes": 15
        },
        // More activities...
    ]
}
```

### Course Analytics Endpoints

#### Get Course Analytics

```http
GET /api/analytics/course-analytics/
```

Get analytics data for courses (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "course_id": 1,
            "course_title": "Introduction to Programming",
            "instructor": "John Smith",
            "enrollment_count": 35,
            "completion_count": 10,
            "average_progress": 45,
            "average_time_spent_hours": 8.5,
            "active_learners_last_week": 25,
            "most_active_module": {
                "id": 3,
                "title": "Control Structures"
            },
            "most_challenging_quiz": {
                "id": 2,
                "title": "Functions and Methods Quiz",
                "pass_rate": 65
            }
        },
        // More courses...
    ]
}
```

### Module Engagement Endpoints

#### Get Module Engagement

```http
GET /api/analytics/module-engagement/
```

Get engagement data for modules (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `course`: Filter by course ID
- `module`: Filter by module ID
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "module_id": 1,
            "module_title": "Getting Started",
            "course_id": 1,
            "course_title": "Introduction to Programming",
            "view_count": 45,
            "completion_count": 30,
            "completion_rate": 66.7,
            "average_time_spent_minutes": 45,
            "student_interactions": 120
        },
        // More modules...
    ]
}
```

### Learner Analytics Endpoints

#### Get Learner Analytics

```http
GET /api/analytics/learner-analytics/
```

Get analytics data for individual learners (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `user`: Filter by user ID
- `course`: Filter by course ID
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 35,
    "next": "http://example.com/api/analytics/learner-analytics/?page=2",
    "previous": null,
    "results": [
        {
            "user_id": 5,
            "username": "student1",
            "full_name": "John Doe",
            "enrolled_courses": 3,
            "completed_courses": 1,
            "average_progress": 55,
            "total_time_spent_hours": 25.5,
            "average_quiz_score": 78,
            "last_login": "2023-06-12T10:30:00Z",
            "activity_trend": "increasing",
            "strengths": ["Python Basics", "Data Structures"],
            "areas_for_improvement": ["Algorithms", "Object-Oriented Programming"]
        },
        // More learners...
    ]
}
```

## QR Codes

### QR Code Endpoints

#### List QR Codes

```http
GET /api/qr-codes/codes/
```

List all QR codes (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `batch`: Filter by batch ID
- `status`: Filter by status (active, expired, revoked)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://example.com/api/qr-codes/codes/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "batch": 1,
            "batch_name": "Fall Semester 2023",
            "type": "attendance",
            "target_id": 1,
            "target_name": "Introduction to Programming - Lecture 1",
            "created_by": 2,
            "created_by_name": "John Smith",
            "status": "active",
            "scan_count": 15,
            "max_scans": 50,
            "expires_at": "2023-06-20T23:59:59Z",
            "created_at": "2023-06-01T08:45:00Z",
            "updated_at": "2023-06-10T14:30:00Z",
            "qr_image_url": "https://example.com/media/qr_codes/550e8400-e29b-41d4-a716-446655440000.png"
        },
        // More QR codes...
    ]
}
```

#### Create QR Code

```http
POST /api/qr-codes/codes/
```

Create a new QR code (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "batch": 1,
    "type": "attendance|certificate|access|module",
    "target_id": 1,
    "max_scans": 50,
    "expires_at": "2023-06-20T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
    "id": 5,
    "uuid": "550e8400-e29b-41d4-a716-446655440123",
    "batch": 1,
    "batch_name": "Fall Semester 2023",
    "type": "attendance",
    "target_id": 1,
    "target_name": "Introduction to Programming - Lecture 1",
    "created_by": 2,
    "created_by_name": "John Smith",
    "status": "active",
    "scan_count": 0,
    "max_scans": 50,
    "expires_at": "2023-06-20T23:59:59Z",
    "created_at": "2023-06-12T08:45:00Z",
    "updated_at": "2023-06-12T08:45:00Z",
    "qr_image_url": "https://example.com/media/qr_codes/550e8400-e29b-41d4-a716-446655440123.png"
}
```

#### Get QR Code Details

```http
GET /api/qr-codes/codes/{id}/
```

Get details of a specific QR code.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: QR code ID

**Response (200 OK):**
```json
{
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "batch": 1,
    "batch_name": "Fall Semester 2023",
    "type": "attendance",
    "target_id": 1,
    "target_name": "Introduction to Programming - Lecture 1",
    "created_by": 2,
    "created_by_name": "John Smith",
    "status": "active",
    "scan_count": 15,
    "max_scans": 50,
    "expires_at": "2023-06-20T23:59:59Z",
    "created_at": "2023-06-01T08:45:00Z",
    "updated_at": "2023-06-10T14:30:00Z",
    "qr_image_url": "https://example.com/media/qr_codes/550e8400-e29b-41d4-a716-446655440000.png",
    "scans": [
        {
            "id": 5,
            "user": 5,
            "user_name": "John Doe",
            "scanned_at": "2023-06-05T10:15:00Z",
            "location": "Lecture Hall A",
            "device_info": "iPhone, Safari 16.0"
        },
        // More scans...
    ]
}
```

#### Update QR Code

```http
PUT /api/qr-codes/codes/{id}/
```

Update a QR code (instructors only).

**Authentication Required:** Yes

**URL Parameters:**
- `id`: QR code ID

**Request Body:**
```json
{
    "status": "active|expired|revoked",
    "max_scans": 100,
    "expires_at": "2023-06-30T23:59:59Z"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "batch": 1,
    "batch_name": "Fall Semester 2023",
    "type": "attendance",
    "target_id": 1,
    "target_name": "Introduction to Programming - Lecture 1",
    "created_by": 2,
    "created_by_name": "John Smith",
    "status": "active",
    "scan_count": 15,
    "max_scans": 100,
    "expires_at": "2023-06-30T23:59:59Z",
    "created_at": "2023-06-01T08:45:00Z",
    "updated_at": "2023-06-12T09:15:00Z",
    "qr_image_url": "https://example.com/media/qr_codes/550e8400-e29b-41d4-a716-446655440000.png"
}
```

#### Delete QR Code

```http
DELETE /api/qr-codes/codes/{id}/
```

Delete a QR code (instructors only).

**Authentication Required:** Yes

**URL Parameters:**
- `id`: QR code ID

**Response (204 No Content):**
Empty response body

### QR Code Scanning Endpoints

#### Record QR Code Scan

```http
POST /api/qr-codes/scans/
```

Record a scan of a QR code.

**Authentication Required:** Yes

**Request Body:**
```json
{
    "qr_code_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "location": "string (optional)",
    "device_info": "string (optional)"
}
```

**Response (201 Created):**
```json
{
    "id": 25,
    "qr_code": 1,
    "qr_code_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "user": 5,
    "user_name": "John Doe",
    "scanned_at": "2023-06-12T10:30:00Z",
    "location": "Lecture Hall A",
    "device_info": "iPhone, Safari 16.0",
    "is_valid": true,
    "validation_message": "Scan recorded successfully",
    "action_performed": "attendance_marked"
}
```

#### List QR Code Scans

```http
GET /api/qr-codes/scans/
```

List QR code scans (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `qr_code`: Filter by QR code ID
- `user`: Filter by user ID
- `is_valid`: Filter by validity (true/false)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 35,
    "next": "http://example.com/api/qr-codes/scans/?page=2",
    "previous": null,
    "results": [
        {
            "id": 25,
            "qr_code": 1,
            "qr_code_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "user": 5,
            "user_name": "John Doe",
            "scanned_at": "2023-06-12T10:30:00Z",
            "location": "Lecture Hall A",
            "device_info": "iPhone, Safari 16.0",
            "is_valid": true,
            "validation_message": "Scan recorded successfully",
            "action_performed": "attendance_marked"
        },
        // More scans...
    ]
}
```

### QR Code Batch Endpoints

#### List QR Code Batches

```http
GET /api/qr-codes/batches/
```

List QR code batches (instructors only).

**Authentication Required:** Yes

**Query Parameters:**
- `type`: Filter by type (attendance, certificate, access, module)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Fall Semester 2023",
            "description": "QR codes for fall semester attendance tracking",
            "type": "attendance",
            "created_by": 2,
            "created_by_name": "John Smith",
            "created_at": "2023-06-01T08:45:00Z",
            "updated_at": "2023-06-01T08:45:00Z",
            "qr_code_count": 25,
            "active_count": 20,
            "scan_count": 150
        },
        // More batches...
    ]
}
```

#### Create QR Code Batch

```http
POST /api/qr-codes/batches/
```

Create a new QR code batch (instructors only).

**Authentication Required:** Yes

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "type": "attendance|certificate|access|module",
    "target_ids": [1, 2, 3],
    "max_scans": 50,
    "expires_at": "2023-06-30T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
    "id": 5,
    "name": "Spring Semester 2024",
    "description": "QR codes for spring semester attendance tracking",
    "type": "attendance",
    "created_by": 2,
    "created_by_name": "John Smith",
    "created_at": "2023-06-12T10:30:00Z",
    "updated_at": "2023-06-12T10:30:00Z",
    "qr_code_count": 3,
    "active_count": 3,
    "scan_count": 0,
    "qr_codes": [
        {
            "id": 10,
            "uuid": "550e8400-e29b-41d4-a716-446655440555",
            "target_id": 1,
            "target_name": "Introduction to Programming - Lecture 1",
            "qr_image_url": "https://example.com/media/qr_codes/550e8400-e29b-41d4-a716-446655440555.png"
        },
        // More QR codes...
    ]
}
```

## Example API Calls

### Authentication Examples

**Register a New User:**
```bash
curl -X POST https://example.com/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Login:**
```bash
curl -X POST https://example.com/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'
```

**Using JWT Token for Authenticated Requests:**
```bash
curl -X GET https://example.com/api/courses/enrolled/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Course Examples

**Get Course Catalog:**
```bash
curl -X GET https://example.com/api/courses/catalog/
```

**Enroll in a Course:**
```bash
curl -X POST https://example.com/api/courses/introduction-to-programming/enroll/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Create a New Course (Instructor):**
```bash
curl -X POST https://example.com/api/courses/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python Programming",
    "description": "Learn advanced Python concepts and best practices",
    "status": "draft",
    "enrollment_type": "open",
    "max_students": 30,
    "start_date": "2023-09-01",
    "end_date": "2023-12-15",
    "course_type": "course"
  }'
```

### Quiz Examples

**Create a Quiz (Instructor):**
```bash
curl -X POST https://example.com/api/quizzes/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "module": 1,
    "title": "Python Basics Quiz",
    "description": "Test your understanding of fundamental Python concepts",
    "instructions": "Answer all questions. You need 70% to pass.",
    "time_limit_minutes": 30,
    "passing_score": 70,
    "randomize_questions": true,
    "allow_multiple_attempts": true,
    "max_attempts": 3,
    "is_published": false,
    "is_survey": false
  }'
```

**Start a Quiz Attempt:**
```bash
curl -X POST https://example.com/api/courses/quizzes/1/start-attempt/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Submit a Question Response:**
```bash
curl -X POST https://example.com/api/courses/quiz-attempts/10/submit-response/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "question": 1,
    "response_data": {
      "selected_choice": 2
    },
    "time_spent_seconds": 45
  }'
```

### QR Code Examples

**Generate a QR Code (Instructor):**
```bash
curl -X POST https://example.com/api/qr-codes/codes/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "type": "attendance",
    "target_id": 1,
    "max_scans": 50,
    "expires_at": "2023-06-30T23:59:59Z"
  }'
```

**Record a QR Code Scan:**
```bash
curl -X POST https://example.com/api/qr-codes/scans/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "qr_code_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "location": "Lecture Hall A",
    "device_info": "iPhone, Safari 16.0"
  }'
```

## Error Codes and Responses

### Common Error Responses

#### 400 Bad Request
```json
{
    "field_name": ["Error message related to this field"]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
    "detail": "Not found."
}
```

#### 429 Too Many Requests
```json
{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Internal server error."
}
```

## API Best Practices

1. **Always Use HTTPS**: All API requests should use HTTPS to ensure data privacy and security.

2. **Token Management**: Store tokens securely and refresh them before they expire to maintain session continuity.

3. **Pagination**: Use the pagination parameters (`page` and `page_size`) for endpoints that return collections to improve performance.

4. **Error Handling**: Implement robust error handling to gracefully manage API errors.

5. **Rate Limiting**: Be aware of rate limits to avoid having requests throttled during high-volume operations.

6. **Filtering**: Use the available filter parameters to reduce the amount of data transferred.

7. **Permissions**: Ensure users have the appropriate permissions before making instructor-only API calls.

8. **Idempotent Operations**: For operations like enrollment, handle idempotent requests appropriately to avoid duplicate actions.