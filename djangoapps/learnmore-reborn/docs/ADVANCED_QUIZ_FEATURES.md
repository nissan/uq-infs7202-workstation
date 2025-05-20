# Advanced Quiz System Features

This document provides an overview of the advanced quiz system features that have been implemented in Phase 6.

## 1. Media Support ✅

Media support for quiz questions has been implemented with the following features:

- **Question Media**: Both questions and answers can now include images
- **External Media URLs**: Support for external media including YouTube videos
- **Responsive Display**: Media is properly displayed in both quiz assessment and results views
- **Lightbox Functionality**: Images can be enlarged for better viewing
- **Accessibility Support**: Alt text and captions for all media

### Implementation details:
- Added image and external_media_url fields to the Question model
- Added image field to the Choice model
- Created the youtube_embed_url filter for converting YouTube URLs to embeds
- Updated templates to properly display media content

## 2. Advanced Time Limits ✅

The quiz timing system has been enhanced with several advanced features:

- **Time Extensions**: Instructors can grant time extensions to individual students
- **Grace Period**: Additional configurable time allowed after the official time limit
- **Improved Timer UI**: Visual countdown with color changes at different thresholds
- **Time Warnings**: Automatic notifications at 75%, 50%, 25%, 10%, and 5% remaining time
- **Auto-save Functionality**: Automatically saves answers when timer runs low

### Implementation details:
- Enhanced the QuizAttempt model with time extension capabilities
- Added API endpoint for instructors to grant extensions
- Updated the quiz-assessment template with improved timer visualization
- Implemented time warning system with auto-save functionality

### API Endpoints:
- `POST /api/courses/quiz-attempts/{id}/grant-extension/` - Grant a time extension for a specific attempt
  - Parameters: `extension_minutes` (int), `reason` (string)
  - Permissions: Instructor only

## 3. Prerequisite Surveys ✅

The quiz system now supports prerequisite relationships between quizzes, with special support for surveys:

- **Survey Prerequisites**: Quizzes can require completion of surveys before access
- **Prerequisite Tracking**: System tracks which prerequisites have been completed
- **Specific Feedback**: Clear indications of which surveys need to be completed
- **Instructor Bypass**: Instructors can optionally bypass prerequisites

### Implementation details:
- Enhanced the QuizPrerequisite model with survey-specific capabilities
- Added methods to detect and display pending survey prerequisites
- Created API endpoint to list all pending surveys across courses
- Updated views to provide clear feedback on prerequisite requirements

### API Endpoints:
- `GET /api/courses/quizzes/pending-surveys/` - List all pending surveys for the current user
- `GET /api/courses/quizzes/{id}/check-prerequisites/` - Check if prerequisites are met for a specific quiz

## 4. Enhanced Feedback ✅

The feedback system has been expanded with multiple levels of feedback and instructor annotations:

- **Conditional Feedback**: Different feedback based on score ranges
- **General Feedback**: Overall quiz feedback for all participants
- **Instructor Annotations**: Ability for instructors to add custom feedback
- **Delayed Feedback**: Option to delay showing feedback until a specified time

### Implementation details:
- Added feedback fields to Quiz and QuestionResponse models
- Created annotation capabilities for instructors
- Implemented conditional feedback based on score ranges
- Added feedback timing controls with delay options

### API Endpoints:
- `POST /api/courses/quiz-attempts/annotate-response/` - Add instructor annotation to a question response
  - Parameters: `response_id` (int), `annotation` (string)
  - Permissions: Instructor only

## Testing Approach

All advanced features are covered by comprehensive tests including:

- **Unit Tests**: Testing model methods and utilities
- **API Tests**: Ensuring API endpoints function correctly with proper permissions
- **Integration Tests**: Verifying complex workflows and interactions

## Future Work

Planned enhancements for the quiz system include:

- Essay Questions with manual grading capabilities
- Advanced Scoring with partial credit and weighted questions
- Analytics Enhancements with item analysis and performance metrics
- Security Enhancements with browser focus detection and session validation
- UI Improvements with preview mode and additional mobile optimizations