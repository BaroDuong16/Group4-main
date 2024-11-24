from django.db import models
from django.conf import settings

# Create your models here.
class Exercise(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('c', 'C'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    language = models.CharField(max_length=10,
                                choices=LANGUAGE_CHOICES,
                                default='python')
    test_cases = models.TextField(help_text="Define test cases as Python/Java/C code")

    def __str__(self):
        return self.title

from assessments.models import Assessment

class Submission(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for user
    email = models.EmailField(null=True, blank=True)  # For anonymous users
    code = models.TextField()
    # created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title}"
