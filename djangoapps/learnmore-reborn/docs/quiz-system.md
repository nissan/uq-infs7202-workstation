# LearnMore Quiz System

This document provides an overview of the LearnMore quiz system. For a more detailed technical description, see [../QUIZ_SYSTEM.md](../QUIZ_SYSTEM.md).

## Overview

The LearnMore Quiz System is a comprehensive assessment framework integrated with the course module system. It provides instructors with tools to create, manage, and analyze quizzes while giving learners an interactive quiz-taking experience.

## Features

- **Multiple question types**: Multiple-choice (single and multiple answer) and True/False questions
- **Customizable quiz parameters**: Time limits, passing scores, attempt limits
- **Randomization options**: Randomize question order to prevent cheating
- **Auto-scoring**: Automatic grading with configurable scoring rules
- **Score normalization**: Normalize scores using Z-score, min-max scaling, and custom methods
- **Detailed feedback**: Per-question explanations and answer feedback
- **Attempt tracking**: Complete history of all quiz attempts
- **Progress integration**: Quiz completion contributes to module progress
- **Time tracking**: Measure time spent on individual questions and entire quizzes
- **Student-friendly UI**: Responsive design with clear navigation

## Quiz Types

The system supports two primary quiz types:

1. **Graded Quizzes**: Traditional assessments with right/wrong answers and passing scores
   - Count toward course completion
   - Support multiple attempt configurations
   - Can be used for summative assessment

2. **Surveys**: Ungraded feedback collection tools
   - Don't count toward course completion
   - All answers are accepted
   - Useful for gathering student opinions and feedback

## Question Types

### Multiple Choice Questions

- Single or multiple correct answers
- Configurable scoring for partially correct answers
- Score normalization across different questions
- Individual feedback for each choice
- Randomizable choice order

### True/False Questions

- Simple binary choice questions
- Clear correct/incorrect feedback
- Useful for quick knowledge checks

## Workflow for Instructors

1. **Creating Quizzes**:
   - Create a quiz associated with a module
   - Configure settings (time limits, passing score, etc.)
   - Add questions and answer choices
   - Provide explanations and feedback
   - Publish when ready

2. **Managing Quizzes**:
   - Edit quiz settings and questions
   - View student attempt data
   - Analyze performance statistics
   - Refine questions based on statistics

## Workflow for Students

1. **Taking Quizzes**:
   - Access quiz from module or quiz list
   - Start attempt (if attempts are available)
   - Answer questions in any order
   - Submit answers as they go (auto-save)
   - Complete quiz manually or automatic completion when time expires

2. **Reviewing Results**:
   - View score and pass/fail status
   - See correct answers and explanations
   - Review individual question feedback
   - Retake quiz if allowed and needed

## Integration with Progress Tracking

The quiz system integrates with the module progress tracking:

- Passing a graded quiz can mark a module as completed
- Quiz completion is recorded in progress statistics
- Time spent on quizzes contributes to total learning time
- Quiz attempts appear in learning analytics

## Best Practices

### For Instructors

- Write clear, unambiguous questions
- Provide helpful explanations for both correct and incorrect answers
- Use appropriate time limits based on question count and complexity
- Test quizzes yourself before publishing
- Review statistics to identify problematic questions
- Use randomization for high-stakes assessments

### For Students

- Read all instructions carefully before starting
- Pay attention to time limits
- Answer the easiest questions first
- Review all answers before submitting if time permits
- Use feedback from quiz attempts to guide further study

## Technical Implementation

For developers interested in the technical details of the quiz system:

- The quiz system is built on Django models with REST API endpoints
- JWT authentication secures all quiz operations
- Responsive templates provide the user interface
- Auto-grading logic handles various question types
- Integration with the progress tracking system through signals and direct updates

For complete technical documentation, see [../QUIZ_SYSTEM.md](../QUIZ_SYSTEM.md).