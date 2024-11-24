from django.db import models
from user.models import User
from course.models import Course

# Create your models here.
class RecommendedCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)  # Optional: if recommendations are user-specific
    reason = models.CharField(max_length=255, blank=True, null=True)  # Reason for the recommendation
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'user')  # Prevent duplicate recommendations for the same user

    def __str__(self):
        return f"{self.course.course_name} recommended for {self.user.username if self.user else 'all users'}"