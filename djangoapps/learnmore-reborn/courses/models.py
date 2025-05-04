from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.title