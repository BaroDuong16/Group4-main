from django.db import models
from user.models import User
from course.models import Course

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_url  = models.CharField(max_length=255, null = True, blank = True)

    def __str__(self):
        return f"{self.course} - {self.user}"