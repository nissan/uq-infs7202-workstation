# User API Documentation

This document describes the available endpoints for user authentication, profile management, and Google OAuth integration.

## Authentication Endpoints

### Register User
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

### Login
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

### Logout
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

### Refresh Token
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

## Profile Management

### Get Profile
```http
GET /api/users/profile/
```

Get the current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
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

### Update Profile
```http
PUT /api/users/profile/
```

Update the current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

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

## Google OAuth Integration

### Google Authentication
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

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "field_name": ["error message"]
}
```

### 401 Unauthorized
```json
{
    "detail": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 60 minutes. Use the refresh token endpoint to get a new access token.

## Rate Limiting

To prevent abuse, the following rate limits are applied:
- Registration: 5 requests per hour per IP
- Login: 20 requests per hour per IP
- Token refresh: 100 requests per hour per IP 