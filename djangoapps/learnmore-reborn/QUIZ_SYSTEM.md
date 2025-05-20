# Quiz System Documentation

## 1. Overview

The LearnMore Quiz System provides a comprehensive assessment framework for course modules. It supports different question types, automatic grading, randomization, time limits, and detailed analytics. The system is designed to be flexible for instructors while providing an engaging experience for learners.

### Key Features

- Multiple choice and true/false questions
- Essay questions with manual grading
- Media support for questions and answers
- Customizable quiz parameters (time limits, passing scores, attempt limits)
- Question randomization
- Automatic grading and feedback
- Enhanced feedback with conditional and delayed options
- Advanced scoring with partial credit and rubrics
- Prerequisite survey system
- Detailed attempt history and analytics
- Integration with module completion tracking
- Responsive UI for all device sizes
- Security enhancements and access controls

## 2. Quiz Models and Relationships

The quiz system is built around these core models:

### Quiz
Central model that belongs to a Module. Contains settings like:
- Title, description, and instructions
- Time limit, grace period, and passing score
- Randomization options
- Attempt limits
- Publication status
- Prerequisites and dependencies

### Question (Abstract Base Class)
Parent class for all question types with:
- Question text and explanation
- Points value
- Order within quiz
- Media support (images, external media)
- Abstract `check_answer()` method

### MultipleChoiceQuestion
Extends Question with:
- Support for multiple correct answers
- Choice ordering
- Individual feedback per choice
- Partial credit options
- Score normalization methods (Z-score, Min-Max, Custom)

### TrueFalseQuestion
Extends Question with:
- Boolean correct answer
- Feedback for each option

### EssayQuestion
Extends Question with:
- Text response field
- Rubric for manual grading
- Instructor feedback field
- Manual grading workflow

### Choice
Belongs to MultipleChoiceQuestion:
- Choice text
- Correctness flag
- Point value (for partial credit)
- Feedback text
- Order within question
- Media support (images)

### QuizAttempt
Tracks a user's session with a quiz:
- Start and completion timestamps
- Status (in_progress, completed, abandoned, timed_out)
- Score and pass/fail status
- Attempt number
- Custom time limit (for accommodations)

### QuestionResponse
Stores user's answer to a specific question:
- Response data (JSON)
- Correctness and points earned
- Time spent on question
- Instructor annotations (for essay questions)

### Relationships

```
Module 1───* Quiz 1───* Question
                           ↑
                           │
           MultipleChoiceQuestion  TrueFalseQuestion  EssayQuestion
                  1                        
                  │                        
                  *                        
               Choice                      

Quiz 1───* QuizAttempt 1───* QuestionResponse *───1 Question
      ↑                                       
      │                                       
      *                                       
     User                                     

Quiz *───* Quiz (prerequisites)
```

## 3. User Roles and Permissions

### Instructors

- Create, edit, and delete quizzes in their own courses
- View all quiz attempts from enrolled students
- Access detailed analytics on quiz performance
- Define quiz parameters (time limits, randomization, etc.)
- Create and manage questions and answer choices
- Grade essay questions and provide feedback
- Manage prerequisites and access controls
- Grant time extensions to students

### Students

- View and take quizzes in enrolled courses
- Review their own attempt history
- See detailed feedback on completed quizzes
- Track progress through course material
- Request time accommodations
- Complete prerequisite surveys before accessing certain quizzes

### Permission Implementation

Permissions are enforced at multiple levels:
- Model-level permissions in viewsets
- URL pattern restrictions
- Template-level conditional rendering
- Object-level permissions for specific quizzes and attempts
- Time-window and IP-based restrictions

## 4. Quiz Workflow

### Creating a Quiz

1. Instructor creates a new quiz associated with a module
2. Quiz settings are configured (time limits, passing score, etc.)
3. Questions are added with appropriate answers and feedback
4. Media is attached to questions and choices as needed
5. Prerequisites are configured if required
6. Once ready, the quiz is marked as published

### Taking a Quiz

1. Student navigates to the quiz detail page
2. System checks prerequisites and access conditions
3. Student initiates the quiz attempt
4. Quiz presents questions (randomized if enabled)
5. Student answers questions and can navigate between them
6. System tracks time spent on each question
7. Quiz is submitted manually or automatically when time expires
8. System grades the attempt and records results
9. Student views detailed feedback (immediately or delayed based on settings)

### Essay Grading Workflow

1. Student submits essay answer as part of quiz attempt
2. System marks the essay as "pending grading"
3. Instructor is notified of pending essay grades
4. Instructor reviews submission against rubric
5. Instructor assigns score and provides feedback
6. Student receives notification that grading is complete
7. Final quiz score is updated to include essay points

### Scoring

1. Each response is evaluated against correct answer(s)
2. Points are awarded based on correctness
   - Full points for completely correct answers
   - Partial credit for partially correct multiple-choice answers
   - Manual scoring for essay questions
3. Total score is calculated as weighted percentage of maximum possible
4. Quiz is marked as passed if score >= passing_score
5. If quiz is passed, associated module may be marked as completed

## 5. API Endpoints

### Quiz Management

- `GET /api/courses/quizzes/` - List quizzes
- `POST /api/courses/quizzes/` - Create quiz
- `GET /api/courses/quizzes/{id}/` - Retrieve quiz details
- `PUT /api/courses/quizzes/{id}/` - Update quiz
- `DELETE /api/courses/quizzes/{id}/` - Delete quiz
- `GET /api/courses/quizzes/{id}/prerequisites/` - List prerequisites
- `POST /api/courses/quizzes/{id}/prerequisites/` - Add prerequisite

### Question Management

- `GET /api/courses/mcquestions/` - List multiple choice questions
- `POST /api/courses/mcquestions/` - Create multiple choice question
- `GET /api/courses/mcquestions/{id}/` - Retrieve question details
- `PUT /api/courses/mcquestions/{id}/` - Update question
- `DELETE /api/courses/mcquestions/{id}/` - Delete question

- `GET /api/courses/tfquestions/` - List true/false questions
- `POST /api/courses/tfquestions/` - Create true/false question
- `GET /api/courses/tfquestions/{id}/` - Retrieve question details
- `PUT /api/courses/tfquestions/{id}/` - Update question
- `DELETE /api/courses/tfquestions/{id}/` - Delete question

- `GET /api/courses/essayquestions/` - List essay questions
- `POST /api/courses/essayquestions/` - Create essay question
- `GET /api/courses/essayquestions/{id}/` - Retrieve question details
- `PUT /api/courses/essayquestions/{id}/` - Update question
- `DELETE /api/courses/essayquestions/{id}/` - Delete question
- `POST /api/courses/essayquestions/{id}/grade/` - Grade essay response

### Quiz Attempt Workflow

- `POST /api/courses/quizzes/{id}/start_attempt/` - Start a new attempt
- `GET /api/courses/quizzes/{id}/attempts/` - List attempts for a quiz
- `GET /api/courses/attempts/{id}/` - Retrieve attempt details
- `POST /api/courses/attempts/{id}/submit_response/` - Submit answer to a question
- `POST /api/courses/attempts/{id}/complete/` - Complete an attempt
- `POST /api/courses/attempts/{id}/timeout/` - Mark attempt as timed out
- `POST /api/courses/attempts/{id}/abandon/` - Abandon an attempt
- `GET /api/courses/attempts/{id}/result/` - View detailed results
- `POST /api/courses/attempts/{id}/extend_time/` - Grant time extension

### Analytics Endpoints

- `GET /api/courses/quizzes/{id}/analytics/` - Get quiz analytics
- `GET /api/courses/questions/{id}/analytics/` - Get question effectiveness
- `GET /api/courses/attempts/analytics/` - Get attempt analytics
- `GET /api/users/analytics/quizzes/` - Get user quiz performance

## 6. Quiz Templating System

The quiz system includes the following templates:

### quiz-list.html
- Displays all available quizzes for enrolled courses
- Includes filtering by course and quiz type
- Shows attempt history information
- Displays prerequisite status
- Responsive card layout

### quiz-detail.html
- Shows detailed quiz information and instructions
- Displays attempt history
- Shows prerequisite requirements
- Provides start button for new attempts
- Shows related quizzes

### quiz-assessment.html
- Interactive quiz-taking interface
- Question navigation system
- Support for text, image, and mixed media questions
- Rich text editor for essay responses
- Timer for time-limited quizzes
- Auto-save functionality

### quiz-results.html
- Detailed feedback on completed attempt
- Shows correct answers and explanations
- Displays score and pass/fail status
- Shows detailed breakdown of scoring
- Option to retake if allowed

### quiz-attempts.html
- Lists all attempts for a quiz
- Shows performance metrics
- Links to detailed results
- Displays time spent statistics

### essay-grading.html
- Instructor interface for grading essays
- Displays student response
- Shows rubric with scoring criteria
- Includes feedback entry field
- Batch grading capabilities

## 7. Quiz Scoring and Progress Tracking

### Scoring Logic

The quiz system scores attempts using these rules:
- Multiple-choice questions can award full or partial points
- True/false questions award full points for the correct answer
- Essay questions are scored manually against a rubric
- Question weights can adjust the value of each question
- Total score is calculated as: `(weighted points earned / maximum weighted points) * 100`
- An attempt is marked as passed if score >= quiz.passing_score

### Progress Tracking Integration

When a quiz is passed:
1. The system checks if it's a survey (not counted for progress) or a regular quiz
2. For regular quizzes, the associated ModuleProgress is updated:
   - Status is set to 'completed'
   - completed_at timestamp is set
3. This may trigger course completion updates if all modules are complete

Code example from `finish_quiz` view:
```python
# Connect to progress tracking if not a survey and passed
if not attempt.quiz.is_survey and is_passed:
    # Get or create progress for this course
    progress, _ = Progress.objects.get_or_create(
        user=attempt.user,
        course=attempt.quiz.module.course
    )
    
    # Update module progress
    module_progress, _ = ModuleProgress.objects.get_or_create(
        progress=progress,
        module=attempt.quiz.module
    )
    
    # Mark module as completed if quiz is passed
    if module_progress.status != 'completed':
        module_progress.status = 'completed'
        module_progress.completed_at = timezone.now()
        module_progress.save()
```

## 8. Advanced Features

### Media Support

The quiz system supports various media types in questions and answers:
- Images embedded directly in questions and choices
- External media URL integration
- Responsive image display
- Lightbox for enlarged viewing
- Accessibility features (alt text, captions)

### Advanced Time Limits

Time management features include:
- Standard quiz-level time limits
- Grace period for submission
- Per-student time accommodations
- Instructor time extensions
- Server-side time validation
- Time tracking per question
- Auto-save on timeout

### Prerequisite Surveys

The prerequisite system controls quiz access:
- Configurable quiz dependencies
- Required completion of surveys before assessments
- Prerequisite status visualization
- Instructor bypass capabilities
- Conditional module progression

### Enhanced Feedback

The feedback system provides:
- General quiz-level feedback
- Question-specific feedback
- Answer-specific feedback
- Conditional feedback based on score ranges
- Delayed feedback release options
- Instructor annotation capabilities
- Rubric-based feedback for essays

### Advanced Scoring

Scoring options include:
- Partial credit for multiple-choice questions
- Individual point values for answer choices
- Negative points for incorrect answers
- Minimum score thresholds
- Weighted questions
- Custom scoring rubrics for essays
- Score normalization options:
  - Z-score normalization (standardizes scores around a mean)
  - Min-Max scaling (transforms scores to a specific range)
  - Percentile ranking (based on historical performance)
  - Custom mapping (for specialized curves and grading scales)

### Security Features

Security enhancements include:
- IP-based access restrictions
- Time window limitations
- Access code protection
- Tab/window focus tracking
- Session timeouts for inactivity
- Randomization of questions and answers
- Question bank drawing

## 9. Best Practices for Creating Quizzes

### Question Writing

- Keep questions clear and concise
- Ensure only one clear correct answer (for single-choice questions)
- Avoid ambiguous wording
- Use consistent formatting
- Include detailed explanations for feedback
- For essay questions, provide clear prompts and expectations

### Quiz Configuration

- Set appropriate time limits based on question count and complexity
- Consider allowing multiple attempts for practice quizzes
- Use randomization for high-stakes assessments
- Set reasonable passing scores (typically 70-80%)
- Test the quiz yourself before publishing
- Establish clear prerequisites for sequential learning

### Media Usage

- Keep images relevant to question content
- Optimize image sizes for web delivery
- Provide descriptive alt text for accessibility
- Consider using images to clarify complex concepts
- Ensure media displays properly on mobile devices

### Performance Considerations

- Avoid creating quizzes with more than 50 questions
- Keep image sizes small for multimedia questions
- Consider breaking very long assessments into multiple quizzes
- Test quiz performance with time limits enabled
- Monitor server load with high-volume quiz taking

### Security

- Randomize questions and answer choices to reduce cheating
- Use time limits for high-stakes assessments
- Consider using question banks with randomized selection
- Monitor unusual patterns in attempt data
- Use IP restrictions for controlled testing environments
- Implement session security for high-stakes exams

### Accessibility

- Write clear, concise question text
- Provide alt text for any images
- Ensure sufficient time for students with accommodations
- Test the quiz interface with screen readers
- Implement high contrast modes for visual impairments
- Support keyboard navigation throughout the quiz interface