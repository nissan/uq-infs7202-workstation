from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Subscription(models.Model):
    SUBSCRIPTION_TYPES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"

class Revenue(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='revenues')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Revenue: ${self.amount} - {self.date.strftime('%Y-%m-%d')}"

class UserActivity(models.Model):
    """Model to track user activities in the system."""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('course_view', 'Course View'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('content_access', 'Content Access'),
        ('profile_update', 'Profile Update'),
        ('settings_change', 'Settings Change'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
