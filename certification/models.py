# certification/models.py
from django.db import models
from django.conf import settings
from course.models import Course
from datetime import datetime

class Certification(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certifications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certifications')
    description = models.TextField(blank=True, null=True)
    awarded_date = models.DateTimeField(null=True, blank=True)
    awarded = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='certifications/', blank=True, null=True)
    generated_html_content = models.TextField(blank=True, null=True)  # Store HTML content if generated dynamically

    def __str__(self):
        return f"Certification: {self.name} for Course: {self.course.course_name} by {self.user}"
