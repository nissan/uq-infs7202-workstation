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

## 5. Essay Questions ✅

Essay questions have been fully implemented, providing support for open-ended responses with manual grading:

- **Rich Text Responses**: Students can provide formatted text answers
- **Manual Grading**: Instructors can review and grade essay responses
- **Rubric System**: Detailed scoring rubrics to guide assessment
- **Partial Credit**: Ability to assign partial points based on response quality
- **Instructor Annotations**: Detailed feedback on specific portions of a response

### Implementation details:
- Created `EssayQuestion` model as a subclass of Question
- Added support for detailed rubrics and scoring guidelines
- Implemented a dedicated grading interface for instructors
- Added annotation capabilities for feedback on specific parts of responses
- Created student-facing views with rich text editing capabilities

### API Endpoints:
- `POST /api/courses/questions/essay/` - Create a new essay question
  - Parameters: `prompt` (string), `points` (int), `rubric` (JSON)
  - Permissions: Instructor only
- `POST /api/courses/quiz-attempts/{id}/grade-essay/` - Provide a grade for an essay response
  - Parameters: `response_id` (int), `points` (float), `feedback` (string)
  - Permissions: Instructor only

## 6. Advanced Scoring ✅

The quiz system now supports sophisticated scoring mechanisms:

- **Partial Credit**: Points can be awarded based on the correctness of a response
- **Weighted Questions**: Questions can have different point values based on importance
- **Score Normalization**: Raw scores can be transformed using statistical methods
- **Rubric-Based Scoring**: Structured evaluation criteria for complex responses
- **Neutral Choices**: Support for survey questions with non-scored options

### Implementation details:
- Enhanced the Choice model with partial credit fields
- Added normalization methods to standardize scores
- Implemented scoring rubrics for complex assessment
- Created detailed score breakdown visualizations
- Added support for non-scored survey responses

### Score Normalization Methods:
- Z-Score Normalization
- Min-Max Scaling
- Percentile Ranking
- Custom Mapping

## 7. Analytics Enhancements ✅

Comprehensive analytics have been added to the quiz system:

- **Question Analytics**: Statistics on question performance and difficulty
- **Quiz Analytics**: Overall quiz effectiveness metrics
- **Student Comparison**: Comparative performance visuals
- **Item Analysis**: Detailed breakdown of response patterns
- **Time Analytics**: Analysis of time spent on questions

### Implementation details:
- Created `QuestionAnalytics` and `QuizAnalytics` models
- Implemented dashboard visualizations for instructors
- Added student-facing performance insights
- Created exportable reports with detailed metrics
- Implemented real-time analytics updates

### API Endpoints:
- `GET /api/courses/quizzes/{id}/analytics/` - Get analytics for a specific quiz
- `GET /api/courses/questions/{id}/analytics/` - Get analytics for a specific question
- `GET /api/analytics/student-comparison/{course_id}/` - Compare student performance in a course

## Testing Approach

All advanced features are covered by comprehensive tests including:

- **Unit Tests**: Testing model methods and utilities
- **API Tests**: Ensuring API endpoints function correctly with proper permissions
- **Integration Tests**: Verifying complex workflows and interactions
- **Performance Tests**: Ensuring analytics scale with large datasets

## Remaining Work

Planned enhancements for the quiz system include:

- **Security Enhancements**: Browser focus detection and session validation
- **UI Improvements**: Complete mobile responsiveness and accessibility features
- **Additional Randomization**: Question banks and block randomization
- **Advanced Session Protection**: Focus tracking and session timeouts