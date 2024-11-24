from django.db import models
from user.models import User
from course.models import Course
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from quiz.models import StudentQuizAttempt
from certification.models import Certification

class ProgressNotification(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    notification_message = models.CharField(max_length=255, blank=True, null=True)
    notification_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

@receiver(post_save, sender=StudentQuizAttempt)
def create_progress_notification(sender, instance, created, **kwargs):
    if created:
        message = f"You finished {instance.quiz.quiz_title} with a score of {instance.score}."
        
        ProgressNotification.objects.create(
            user=instance.user,
            course=instance.quiz.course, 
            notification_message=message
        )
@receiver(post_save, sender=Certification)
def create_progress_notification_certificate(sender, instance, created, **kwargs):
    if created:
        message = f"Congratulations, Certificate is Ready!"
        
        ProgressNotification.objects.create(
            user=instance.user,
            course=instance.course, 
            notification_message=message
        )

@receiver(post_delete, sender=StudentQuizAttempt)
def delete_progress_notification(sender, instance, **kwargs):
    ProgressNotification.objects.filter(user=instance.user, course=instance.quiz.course).delete()