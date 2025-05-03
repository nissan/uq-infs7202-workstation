from django.db import models
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Content

User = get_user_model()

class TutorSession(models.Model):
    """Model to track AI tutor sessions."""
    SESSION_TYPES = [
        ('course', 'Course'),
        ('module', 'Module'),
        ('content', 'Content'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_sessions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutor_sessions')
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutor_sessions')
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutor_sessions')
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='general')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    llm_model = models.CharField(max_length=50, default='default')  # to track which LLM was used
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['course', 'session_type']),
        ]
    
    def __str__(self):
        if self.title:
            return self.title
        
        if self.course:
            return f"Session for {self.course.title}"
        
        return f"Session by {self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def get_context_items(self):
        """Get context items relevant to this session."""
        return TutorContextItem.objects.filter(session=self).order_by('order')

class TutorContextItem(models.Model):
    """Model to store context items for a session."""
    CONTEXT_TYPES = [
        ('course', 'Course'),
        ('module', 'Module'),
        ('content', 'Content'),
        ('custom', 'Custom'),
    ]
    
    session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='context_items')
    context_type = models.CharField(max_length=10, choices=CONTEXT_TYPES)
    content_object_id = models.PositiveIntegerField(null=True, blank=True)  # ID of related object
    title = models.CharField(max_length=255)
    content = models.TextField()  # The actual content to be used as context
    relevance_score = models.FloatField(default=1.0)  # For ranking context items
    order = models.PositiveIntegerField(default=0)  # For ordering items
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-relevance_score']
        indexes = [
            models.Index(fields=['session', 'order']),
            models.Index(fields=['context_type', 'content_object_id']),
        ]
    
    def __str__(self):
        return self.title

class TutorMessage(models.Model):
    """Model to store conversation messages."""
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tokens_used = models.PositiveIntegerField(default=0)  # For tracking token usage
    relevant_context_used = models.ManyToManyField(TutorContextItem, blank=True, related_name='used_in_messages')
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        return f"{self.message_type} message in {self.session}"

class ContentEmbedding(models.Model):
    """Model to store vector embeddings for content."""
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name='embedding')
    embedding_vector = models.TextField()  # JSON-serialized embedding vector
    chunk_text = models.TextField()  # The text chunk that was embedded
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['content']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Embedding for {self.content}"