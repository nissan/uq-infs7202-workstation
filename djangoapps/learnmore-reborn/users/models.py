from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extended user profile model that adds additional fields to Django's built-in User model.
    This model is automatically created/updated when a User is created/updated.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    student_id = models.CharField(max_length=20, blank=True, help_text="Student ID number if applicable")
    department = models.CharField(max_length=100, blank=True, help_text="Department or faculty")
    is_instructor = models.BooleanField(default=False, help_text="Whether this user can create and manage courses")
    google_id = models.CharField(max_length=100, blank=True, help_text="Google OAuth ID if user signs in with Google")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create/update the UserProfile when a User is created/updated.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
