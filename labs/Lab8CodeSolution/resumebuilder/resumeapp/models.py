from django.db import models

from django.contrib.auth.models import User
from django.db import models

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django's built-in User model
    firstname = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=False, default="Novice Django Developer but building unique portfolio")  # <-- NEW FIELD

    def __str__(self):
        return f"Details for {self.user.username}"

class Qualification(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)  # One user can have many qualifications
    title = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    date_completed = models.DateField()

    def __str__(self):
        return f"{self.title} from {self.university} (User: {self.user.user.username})"


class WorkExperience(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)  # One user can have many jobs
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # Can be blank for current jobs
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company} (User: {self.user.user.username})"