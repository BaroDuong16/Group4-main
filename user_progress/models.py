from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from quiz.models import Quiz, StudentQuizAttempt
from collections import Counter
from course.models import Course, Enrollment

# Create your models here.
class UserProgress(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)  # String reference to avoid circular import
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_accessed = models.DateTimeField(auto_now=True)  # Updated to reflect last accessed time

    class Meta:
        unique_together = ('user', 'course')
        db_table = 'progress_progress'

    def __str__(self):
        return f"{self.user} - {self.course} - {self.progress_percentage}%"

def calculate(user_id, course_id):
    quizzes = Quiz.objects.filter(course=course_id).count()
    attempts = len(Counter(set(
        StudentQuizAttempt.objects.filter(user=user_id, quiz__course=course_id).values_list('quiz_id', flat=True)
        )))
    return quizzes, attempts


@receiver([post_save, post_delete], sender=Quiz)
def update_quiz_progress(sender, instance, **kwargs):

    enrollments = Enrollment.objects.filter(course=instance.course)
    for enrollment in enrollments:
        user_id = enrollment.student.id
        total, attempts = calculate(user_id, instance.course.id)
        
        percent = round(attempts / total * 100, 2) if total > 0 else 0
        
        progress, created = UserProgress.objects.get_or_create(
            user=enrollment.student,
            course=instance.course
        )
        progress.progress_percentage = percent
        progress.save()

@receiver(post_save, sender=StudentQuizAttempt)
def update_user_progress(sender, instance, **kwargs):

    user_id = instance.user.id
    course_id = instance.quiz.course.id
    total, attempts = calculate(user_id, course_id)
    
    percent = round(attempts / total * 100, 2) if total > 0 else 0
    
    progress, _ = UserProgress.objects.get_or_create(
        user=instance.user,
        course=instance.quiz.course
    )
    progress.progress_percentage = percent
    progress.save()


@receiver([post_save, post_delete], sender=Enrollment)
def update_enrollment_progress(sender, instance, **kwargs):
    if kwargs.get('created', False):  # Sự kiện post_save
        user_id = instance.student.id
        course_id = instance.course.id
        total, attempts = calculate(user_id, course_id)
        
        percent = round(attempts / total * 100, 2) if total > 0 else 0
        

        progress, _ = UserProgress.objects.get_or_create(
            user=instance.student,
            course=instance.course
        )
        progress.progress_percentage = percent
        progress.save()
    
    # Kiểm tra nếu là post_delete
    else:  # Sự kiện post_delete
        user_id = instance.student.id
        course_id = instance.course.id
        UserProgress.objects.filter(user=instance.student, course=instance.course).delete()