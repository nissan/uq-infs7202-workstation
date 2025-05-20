from django.db import models
from django.conf import settings
from courses.models import Course, Module, Quiz

class TutorKnowledgeBase(models.Model):
    """Model for storing knowledge base content for the AI tutor."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='knowledge_bases', null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='knowledge_bases', null=True, blank=True)
    vector_embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tutor Knowledge Base"
        verbose_name_plural = "Tutor Knowledge Bases"
    
    def __str__(self):
        return self.title

class TutorSession(models.Model):
    """Model for storing AI tutor session data."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tutor_sessions', null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='tutor_sessions', null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='tutor_sessions', null=True, blank=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    session_context = models.JSONField(default=dict, help_text="Contextual data for the session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tutor Session"
        verbose_name_plural = "Tutor Sessions"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class TutorMessage(models.Model):
    """Model for storing messages in an AI tutor conversation."""
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('tutor', 'Tutor'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata for the message")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tutor Message"
        verbose_name_plural = "Tutor Messages"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type} message in {self.session}"

class TutorFeedback(models.Model):
    """Model for storing user feedback on AI tutor interactions."""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_feedback')
    message = models.ForeignKey(TutorMessage, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    comment = models.TextField(blank=True)
    helpful = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tutor Feedback"
        verbose_name_plural = "Tutor Feedback"
    
    def __str__(self):
        return f"Feedback on {self.session} by {self.user.username}"

class TutorConfiguration(models.Model):
    """Model for storing AI tutor configuration settings."""
    name = models.CharField(max_length=255)
    model_provider = models.CharField(max_length=50, default='openai')
    model_name = models.CharField(max_length=50, default='gpt-3.5-turbo')
    temperature = models.FloatField(default=0.7)
    max_tokens = models.PositiveIntegerField(default=1000)
    system_prompt = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tutor Configuration"
        verbose_name_plural = "Tutor Configurations"
    
    def __str__(self):
        return self.name