from django.db import models
from user.models import User
from course.models import Course

class AIInsights(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    insight_text = models.CharField(max_length=255, blank=True, null=True)
    insight_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.course} - {self.insight_text} - {self.insight_type}"
    
    def save(self, *args, **kwargs):
        for fields in ['insight_text', 'insight_type']:
            val = getattr(self, fields, False)
            if val:
                setattr(self, fields, val.capitalize().strip())
        super(AIInsights, self).save(*args, **kwargs)