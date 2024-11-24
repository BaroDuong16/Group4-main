from django.db import models
from django.conf import settings
from course.models import Course  # Assuming `Course` is imported from the `course` app




class ArchivedCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='archived_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_archived = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} archived {self.course.course_name}"


class LearningTool(models.Model):
    TOOL_TYPE_CHOICES = [
        ('video', 'Video'),
        ('document', 'Document'),
        ('quiz', 'Quiz'),
        ('interactive', 'Interactive Tool'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPE_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_tools', null=True, blank=True)
    link = models.URLField(max_length=500, blank=True, null=True)  # Link to the tool/resource
    file = models.FileField(upload_to='learning_tools/', blank=True, null=True)

    def __str__(self):
        return f"Tool: {self.title} for Course: {self.course.course_name if self.course else 'General'}"
