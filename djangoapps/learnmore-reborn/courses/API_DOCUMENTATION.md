# Course Catalog and Enrollment API Documentation

This document provides details on the Course Catalog and Enrollment API endpoints available in the LearnMore system.

## Course Catalog Endpoints

### List Published Courses (Catalog)

Lists all published courses available for enrollment.

**Endpoint:** `GET /api/courses/catalog/`

**Authentication:** Not required

**Query Parameters:**
- `enrollment_type`: Filter by enrollment type (options: "open", "restricted")
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response:**

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
    ...
  ]
}
```

### Search Courses

Search for courses by title or description.

**Endpoint:** `GET /api/courses/catalog/search/`

**Authentication:** Not required

**Query Parameters:**
- `q`: Search query string (required)
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Response:** Same format as the catalog endpoint

## Enrollment Endpoints

### Enroll in Course

Enrolls the authenticated user in a specific course.

**Endpoint:** `POST /api/courses/{slug}/enroll/`

**Authentication:** Required

**URL Parameters:**
- `slug`: Course slug to enroll in

**Response:**

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

**Error Responses:**
- `400 Bad Request`: If the user is already enrolled, the course is not published, or the course is full

### Unenroll from Course

Unenrolls the authenticated user from a specific course.

**Endpoint:** `POST /api/courses/{slug}/unenroll/`

**Authentication:** Required

**URL Parameters:**
- `slug`: Course slug to unenroll from

**Response:**
- `204 No Content`: If successful

**Error Responses:**
- `400 Bad Request`: If the user is not enrolled in the course

### List Enrolled Courses

Lists all courses the authenticated user is actively enrolled in.

**Endpoint:** `GET /api/courses/enrolled/`

**Authentication:** Required

**Response:**

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
  ...
]
```

## Enrollment Management

### Enrollment Model

The `Enrollment` model tracks student enrollment in courses with the following fields:

- `user`: The enrolled user
- `course`: The course being enrolled in
- `status`: Enrollment status (active, completed, dropped)
- `progress`: Percentage completion (0-100)
- `enrolled_at`: Date and time of enrollment
- `completed_at`: Date and time of completion (if completed)

### Enrollment Status

Enrollment can have the following statuses:

- `active`: User is currently enrolled and has access to course content
- `completed`: User has completed the course
- `dropped`: User has unenrolled from the course

### Course Enrollment Types

Courses can have the following enrollment types:

- `open`: Anyone can enroll
- `restricted`: Enrollment requires approval or an invitation code

### Course Capacity Management

Courses can have a maximum enrollment capacity:

- If `max_students` is greater than 0, the course has a limited capacity
- If `max_students` is 0, the course has unlimited enrollment capacity
- The `is_full` property indicates whether a course has reached its capacity