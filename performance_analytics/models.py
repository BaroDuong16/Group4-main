from django.db import models
from course.models import Course
from quiz.models import Quiz,StudentQuizAttempt
from user.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.db.models import OuterRef, Subquery,Max
# Create your models here.
class PerformanceAnalytics(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    average_score = models.FloatField(default=0.0)
    completion_rate = models.IntegerField(default=0.0)

    def update_performance(self):
        # quiz = PerformanceAnalytics.objects.filter(course = self.course.id)
        latest_attempt_dates = StudentQuizAttempt.objects.filter(
            user=self.user, quiz = OuterRef('quiz')
        ).values('quiz').annotate(latest_date=Max('attempt_date')).values('latest_date')

        latest_attempts = StudentQuizAttempt.objects.filter(
            user=self.user,
            quiz__course=self.course,
            attempt_date__in=Subquery(latest_attempt_dates)
        )
        
        total_quizzes = Quiz.objects.filter(course = self.course).count()
        if total_quizzes > 0:
            total_score = latest_attempts.aggregate(models.Sum('score'))['score__sum'] or 0
            self.average_score = round(total_score / total_quizzes,3)
            completed_quizzes = latest_attempts.filter(score__gt=0).count()
            self.completion_rate = round(completed_quizzes / total_quizzes,2) *100
        else:
            self.average_score = 0.0
            self.completion_rate = 0.0
        self.save()
    
    class Meta:
        db_table = 'performance' 

@receiver(post_save, sender=StudentQuizAttempt)
@receiver(post_delete, sender=StudentQuizAttempt )
def update_performance_analytics(sender, instance, **kwargs):
    try:
        performance = PerformanceAnalytics.objects.get( user = instance.user,course = instance.quiz.course)
    except PerformanceAnalytics.DoesNotExist:
        performance = PerformanceAnalytics( user= instance.user,course = instance.quiz.course)
    performance.update_performance()


@receiver(post_save, sender=Quiz)
@receiver(post_delete, sender=Quiz)
def update_completion_rate(sender, instance, **kwargs):
    
        students = User.objects.filter(profile__role__role_name='student', enrollment__course=instance.course)
        for student in students:
            try:
                performance = PerformanceAnalytics.objects.get( user= student,course = instance.course)
            except PerformanceAnalytics.DoesNotExist:
                performance = PerformanceAnalytics( user = student,course = instance.course)
            performance.update_performance()
    