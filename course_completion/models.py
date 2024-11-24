from django.db import models
from user.models import User
from course.models import Course
# from Performance_Analytics.models import PerformanceAnalytics

# Create your models here.
class CourseCompletion(models.Model):
    completion_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    completion_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Course_Completion'