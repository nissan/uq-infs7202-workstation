# Progress Tracking & Learning Interface

The LearnMore platform features a comprehensive learning progress tracking system with a user-friendly interface for learners to navigate course content and track their progress.

## Features

### Progress Tracking

- **Course Progress**: Track overall completion percentage across an entire course
- **Module Tracking**: Track individual module completion status and time spent
- **Prerequisite Management**: Enforce completion requirements before accessing subsequent modules
- **Time Tracking**: Automatic tracking of time spent on each module
- **Learning Statistics**: Detailed statistics about learning activities and progress

### Learning Interface

- **Module Navigation**: Intuitive navigation between course modules
- **Progress Indicators**: Visual feedback on completion status
- **Content Position Tracking**: Remember position in videos, readings, etc.
- **Continue Learning**: Quick access to pick up where you left off
- **Responsive Design**: Works on all screen sizes and devices

## Models

### Progress Model

The `Progress` model tracks a user's overall progress in a specific course:

```python
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress_records')
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    total_duration_seconds = models.PositiveIntegerField(default=0)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_completed = models.BooleanField(default=False)

    # ...methods for updating completion percentage, etc.
```

### ModuleProgress Model

The `ModuleProgress` model tracks a user's progress on a specific module:

```python
class ModuleProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    progress = models.ForeignKey(Progress, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    last_activity = models.DateTimeField(auto_now=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    content_position = models.JSONField(default=dict)

    # ...methods for marking as complete, tracking time, etc.
```

## API Endpoints

### Progress API

The following endpoints are available for progress tracking:

- `GET /api/progress/progress/` - List user's progress records
- `GET /api/progress/progress/{id}/` - Get details about a specific progress record
- `GET /api/progress/progress/course/?course_id={id}` - Get progress for a specific course
- `GET /api/progress/progress/continue_learning/` - Get next module to continue learning
- `GET /api/progress/progress/stats/` - Get learning statistics
- `POST /api/progress/progress/{id}/reset/` - Reset progress for a course

### Module Progress API

- `GET /api/progress/module-progress/` - List user's module progress records
- `GET /api/progress/module-progress/{id}/` - Get details about a specific module progress
- `POST /api/progress/module-progress/{id}/complete/` - Mark a module as completed
- `POST /api/progress/module-progress/{id}/update_position/` - Update content position
- `POST /api/progress/module-progress/{id}/add_time/` - Add time spent on a module

## UI Components

The learning interface includes the following key UI components:

1. **Learning Interface**: Main UI for viewing module content and tracking progress
   - Template: `progress/templates/progress/learning-interface.html`

2. **Statistics Dashboard**: UI for viewing learning statistics
   - Template: `progress/templates/progress/learning-statistics.html`

3. **Course Progress**: Display of progress for a specific course
   - Template: `progress/templates/progress/course-progress.html`

## Usage Examples

### Tracking Module Completion

```javascript
// JavaScript example from the learning interface
document.addEventListener('DOMContentLoaded', function() {
    // Mark a module as completed
    const completeButton = document.getElementById('complete-module');
    if (completeButton) {
        completeButton.addEventListener('click', function() {
            const moduleProgressId = completeButton.dataset.progressId;
            fetch(`/api/progress/module-progress/${moduleProgressId}/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update UI to show completion status
                updateCompletionUI(data.course_completion_percentage);
            });
        });
    }
});
```

### Time Tracking

Time spent on modules is automatically tracked when the user views a module. The system:

1. Starts a timer when the user loads a module
2. Periodically updates the server with time spent using the `add_time` endpoint
3. Sends a final update when the user navigates away from the page

### Prerequisites

Modules can have prerequisites defined by the instructor. The system checks if all prerequisites have been completed before allowing access to a module:

```python
def is_accessible(self, user):
    """
    Check if the module is accessible to the user.
    A module is accessible if:
    1. It has no prerequisites, or
    2. All its prerequisites have been completed by the user
    """
    if not self.has_prerequisites:
        return True
        
    # Get the progress record for the user and course
    from progress.models import Progress, ModuleProgress
    try:
        progress = Progress.objects.get(user=user, course=self.course)
    except Progress.DoesNotExist:
        return False
        
    # Check if all prerequisites are completed
    prereq_modules = self.get_prerequisite_modules()
    completed_prereqs = ModuleProgress.objects.filter(
        progress=progress,
        module__in=prereq_modules,
        status='completed'
    ).count()
    
    return completed_prereqs == prereq_modules.count()
```

## Testing

The progress tracking system includes comprehensive tests:

1. **Model Tests**: Test the Progress and ModuleProgress models
2. **API Tests**: Test the progress tracking API endpoints
3. **Integration Tests**: End-to-end tests for learning workflow
4. **UI Tests**: Test the learning interface and statistics dashboard

To run the tests:

```bash
# Run all progress tests
python manage.py test progress

# Run specific test modules
python manage.py test progress.tests.test_models
python manage.py test progress.tests.test_api
python manage.py test progress.tests.test_integration
```