from django.db import models
from user.models import User
from course.models import Course
from assessments.models import Assessment
# from assignment.models import Assignment
from quiz.models import Quiz

class StudentPerformance(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)  # No foreign key constraint
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # No foreign key constraint
    # quiz = models.IntegerField(Quiz, blank=True)  # Optional quiz reference, no foreign key
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE,null=True, blank=True)  # Optional assignment reference, no foreign key
    # assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE,null=True, blank=True)  # Optional assignment reference, no foreign key
    score = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.performance_id)
