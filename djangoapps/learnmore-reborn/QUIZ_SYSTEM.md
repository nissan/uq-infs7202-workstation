# Quiz System Documentation

## 1. Overview

The LearnMore Quiz System provides a comprehensive assessment framework for course modules. It supports different question types, automatic grading, randomization, time limits, and detailed analytics. The system is designed to be flexible for instructors while providing an engaging experience for learners.

### Key Features

- Multiple choice and true/false questions
- Customizable quiz parameters (time limits, passing scores, attempt limits)
- Question randomization
- Automatic grading and feedback
- Detailed attempt history and analytics
- Integration with module completion tracking
- Responsive UI for all device sizes

## 2. Quiz Models and Relationships

The quiz system is built around these core models:

### Quiz
Central model that belongs to a Module. Contains settings like:
- Title, description, and instructions
- Time limit and passing score
- Randomization options
- Attempt limits
- Publication status

### Question (Abstract Base Class)
Parent class for all question types with:
- Question text and explanation
- Points value
- Order within quiz
- Abstract `check_answer()` method

### MultipleChoiceQuestion
Extends Question with:
- Support for multiple correct answers
- Choice ordering
- Individual feedback per choice

### TrueFalseQuestion
Extends Question with:
- Boolean correct answer

### Choice
Belongs to MultipleChoiceQuestion:
- Choice text
- Correctness flag
- Feedback text
- Order within question

### QuizAttempt
Tracks a user's session with a quiz:
- Start and completion timestamps
- Status (in_progress, completed, abandoned, timed_out)
- Score and pass/fail status
- Attempt number

### QuestionResponse
Stores user's answer to a specific question:
- Response data (JSON)
- Correctness and points earned
- Time spent on question

### Relationships

```
Module 1───* Quiz 1───* Question
                           ↑
                           │
           MultipleChoiceQuestion  TrueFalseQuestion
                  1                        
                  │                        
                  *                        
               Choice                      

Quiz 1───* QuizAttempt 1───* QuestionResponse *───1 Question
      ↑                                       
      │                                       
      *                                       
     User                                     
```

## 3. User Roles and Permissions

### Instructors

- Create, edit, and delete quizzes in their own courses
- View all quiz attempts from enrolled students
- Access detailed analytics on quiz performance
- Define quiz parameters (time limits, randomization, etc.)
- Create and manage questions and answer choices

### Students

- View and take quizzes in enrolled courses
- Review their own attempt history
- See detailed feedback on completed quizzes
- Track progress through course material

### Permission Implementation

Permissions are enforced at multiple levels:
- Model-level permissions in viewsets
- URL pattern restrictions
- Template-level conditional rendering
- Object-level permissions for specific quizzes and attempts

## 4. Quiz Workflow

### Creating a Quiz

1. Instructor creates a new quiz associated with a module
2. Quiz settings are configured (time limits, passing score, etc.)
3. Questions are added with appropriate answers and feedback
4. Once ready, the quiz is marked as published

### Taking a Quiz

1. Student navigates to the quiz detail page
2. Student initiates the quiz attempt
3. Quiz presents questions (randomized if enabled)
4. Student answers questions and can navigate between them
5. Quiz is submitted manually or automatically when time expires
6. System grades the attempt and records results
7. Student views detailed feedback

### Scoring

1. Each response is evaluated against correct answer(s)
2. Points are awarded based on correctness
3. Total score is calculated as percentage of maximum possible
4. Quiz is marked as passed if score >= passing_score
5. If quiz is passed, associated module may be marked as completed

## 5. API Endpoints

### Quiz Management

- `GET /api/courses/quizzes/` - List quizzes
- `POST /api/courses/quizzes/` - Create quiz
- `GET /api/courses/quizzes/{id}/` - Retrieve quiz details
- `PUT /api/courses/quizzes/{id}/` - Update quiz
- `DELETE /api/courses/quizzes/{id}/` - Delete quiz

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

### Quiz Attempt Workflow

- `POST /api/courses/quizzes/{id}/start_attempt/` - Start a new attempt
- `GET /api/courses/quizzes/{id}/attempts/` - List attempts for a quiz
- `GET /api/courses/attempts/{id}/` - Retrieve attempt details
- `POST /api/courses/attempts/{id}/submit_response/` - Submit answer to a question
- `POST /api/courses/attempts/{id}/complete/` - Complete an attempt
- `POST /api/courses/attempts/{id}/timeout/` - Mark attempt as timed out
- `POST /api/courses/attempts/{id}/abandon/` - Abandon an attempt
- `GET /api/courses/attempts/{id}/result/` - View detailed results

## 6. Quiz Templating System

The quiz system includes the following templates:

### quiz-list.html
- Displays all available quizzes for enrolled courses
- Includes filtering by course and quiz type
- Shows attempt history information
- Responsive card layout

### quiz-detail.html
- Shows detailed quiz information and instructions
- Displays attempt history
- Provides start button for new attempts
- Shows related quizzes

### quiz-assessment.html
- Interactive quiz-taking interface
- Question navigation system
- Timer for time-limited quizzes
- Auto-save functionality

### quiz-results.html
- Detailed feedback on completed attempt
- Shows correct answers and explanations
- Displays score and pass/fail status
- Option to retake if allowed

### quiz-attempts.html
- Lists all attempts for a quiz
- Shows performance metrics
- Links to detailed results

## 7. Quiz Scoring and Progress Tracking

### Scoring Logic

The quiz system scores attempts using these rules:
- Multiple-choice questions award full points for selecting all correct answers
- True/false questions award full points for the correct answer
- Partial credit may be awarded for some multiple-choice questions
- Total score is calculated as: `(points earned / maximum points) * 100`
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

## 8. Best Practices for Creating Quizzes

### Question Writing

- Keep questions clear and concise
- Ensure only one clear correct answer (for single-choice questions)
- Avoid ambiguous wording
- Use consistent formatting
- Include detailed explanations for feedback

### Quiz Configuration

- Set appropriate time limits based on question count and complexity
- Consider allowing multiple attempts for practice quizzes
- Use randomization for high-stakes assessments
- Set reasonable passing scores (typically 70-80%)
- Test the quiz yourself before publishing

### Performance Considerations

- Avoid creating quizzes with more than 50 questions
- Keep image sizes small for multimedia questions
- Consider breaking very long assessments into multiple quizzes
- Test quiz performance with time limits enabled

### Security

- Randomize questions and answer choices to reduce cheating
- Use time limits for high-stakes assessments
- Consider using question banks with randomized selection
- Monitor unusual patterns in attempt data

### Accessibility

- Write clear, concise question text
- Provide alt text for any images
- Ensure sufficient time for students with accommodations
- Test the quiz interface with screen readers