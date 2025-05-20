# Progress Tracking Implementation

This document provides an overview of the progress tracking system implemented in the LearnMore application.

## Overview

The progress tracking system allows users to track their learning journey through courses, including:

- Overall course completion progress
- Individual module completion status
- Time spent on learning activities
- Tracking prerequisites for modules
- Resuming learning where they left off
- Viewing learning statistics

## Models

### Progress

The `Progress` model tracks a user's overall progress in a specific course:

```python
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress_records')
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    total_duration_seconds = models.PositiveIntegerField(default=0, help_text='Total time spent on course in seconds')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_completed = models.BooleanField(default=False)
```

Key methods:
- `update_completion()`: Updates completion status based on module progress
- `add_duration(seconds)`: Adds time spent to the total duration
- `calculate_completion_percentage()`: Calculates the percentage of completed modules
- `next_module`: Property that returns the next incomplete module in the course

### ModuleProgress

The `ModuleProgress` model tracks a user's progress within a specific module:

```python
class ModuleProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    progress = models.ForeignKey(Progress, on_delete=models.CASCADE, related_name='module_progress_records')
    module = models.ForeignKey('courses.Module', on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    content_position = models.JSONField(null=True, blank=True, help_text='Position in video/audio content or last page viewed')
    duration_seconds = models.PositiveIntegerField(default=0, help_text='Time spent on this module in seconds')
    last_activity = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

Key methods:
- `mark_completed()`: Marks a module as completed and updates the parent Progress
- `update_content_position(position_data)`: Updates the saved position in content (e.g., video timestamp)
- `add_duration(seconds)`: Adds time spent to the module and updates the parent Progress

## API Endpoints

The progress tracking system exposes several API endpoints:

### Progress Endpoints

- `GET /api/progress/progress/` - List all progress records for the current user
- `GET /api/progress/progress/{id}/` - Get details for a specific progress record
- `GET /api/progress/progress/course/?course_id={id}` - Get progress for a specific course
- `GET /api/progress/progress/continue_learning/` - Get the next incomplete module to continue learning
- `GET /api/progress/progress/stats/` - Get learning statistics across all courses
- `POST /api/progress/progress/{id}/reset/` - Reset progress for a specific course

### ModuleProgress Endpoints

- `GET /api/progress/module-progress/` - List all module progress records for the current user
- `GET /api/progress/module-progress/{id}/` - Get details for a specific module progress record
- `POST /api/progress/module-progress/{id}/complete/` - Mark a module as completed
- `POST /api/progress/module-progress/{id}/update_position/` - Update content position (for video/audio)
- `POST /api/progress/module-progress/{id}/add_time/` - Add time spent on a module

## UI Components

### Learning Interface

The learning interface (`learning-interface.html`) provides a comprehensive environment for consuming course content, with features including:

- Module content display with responsive design
- Progress indicator showing completion percentage
- Navigation between modules
- Time tracking of learning activity
- Module completion button
- Prerequisites display and verification
- Content position tracking for video/audio content

### Progress Tracking Views

The system includes several views for tracking and displaying progress:

- `Learning Statistics`: Shows overall learning stats across all courses
- `Course Progress`: Shows detailed progress for a specific course
- `Learner Progress`: Shows a summary of progress across all enrolled courses

### Reset Confirmation UI

A modal confirmation dialog is displayed when a user attempts to reset their progress, including:

- Warning about data loss
- Summary of current progress
- Confirmation and cancel buttons
- Loading state during the reset process

## Frontend Integration

The frontend integrates with the backend APIs to provide a seamless user experience:

- Automatic time tracking of learning activities
- Real-time progress updates as modules are completed
- Content position tracking for video/audio content
- Continue learning from where the user left off
- Filtering courses by completion status

## Implementation Notes

1. **Time Tracking**: Time is tracked automatically while the user is viewing module content and sent to the server when they navigate away.

2. **Prerequisites**: Modules can have prerequisites that must be completed before the module becomes accessible. This is enforced at both the UI and API levels.

3. **Content Position**: For video and audio content, the system tracks the user's position so they can resume where they left off.

4. **Progress Reset**: Users can reset their progress for a course, which deletes all module progress records and resets the completion percentage to 0.

5. **Access Control**: Progress records are user-specific, and users can only access their own progress data.

## Usage Guidelines

### Setting Module Prerequisites

In the admin interface or course editor, you can define prerequisites for modules:

1. Navigate to a module's edit page
2. Use the prerequisites field to select other modules that must be completed
3. Save the module

### Tracking User Progress

Progress is tracked automatically when users:

1. View a module for the first time (status changes to 'in_progress')
2. Click the 'Mark as Complete' button (status changes to 'completed')
3. Navigate away from a module (time spent is updated)

### Resetting Progress

Users can reset their progress by:

1. Navigating to the course progress page or learning statistics
2. Clicking the 'Reset Progress' button
3. Confirming in the modal dialog

## Integration with Quiz System

The progress tracking system is designed to integrate with the quiz system. When a user completes a quiz:

1. The corresponding module can be marked as completed
2. The time spent on the quiz can be added to the module's duration
3. The completion status updates the overall course progress

## Edge Cases and Error Handling

- If a module becomes inaccessible due to a prerequisite change, its progress is preserved
- If a course's modules change, the progress record is automatically updated with the new total
- Time tracking has safeguards against unrealistic session lengths
- Concurrent updates are handled safely through transaction management