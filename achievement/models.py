from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from collections import Counter
from course.models import Course, Enrollment
from assessments.models import Assessment, StudentAssessmentAttempt
from django.db.models import OuterRef, Subquery,Max
from user.models import User
#########################################################################################################
class UserProgress(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)  # String reference to avoid circular import
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_accessed = models.DateTimeField(auto_now=True)  # Updated to reflect last accessed time

    class Meta:
        unique_together = ('user', 'course')
        db_table = 'achievement_progress'

    def __str__(self):
        return f"{self.user} - {self.course} - {self.progress_percentage}%"
    
def calculate(user_id, course_id):
    quizzes = Assessment.objects.filter(course=course_id).count()
    attempts = len(Counter(set(
        StudentAssessmentAttempt.objects.filter(user=user_id, assessment__course=course_id).values_list('assessment_id', flat=True)
        )))
    return quizzes, attempts

@receiver([post_save, post_delete], sender=Assessment)
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

@receiver(post_save, sender=StudentAssessmentAttempt)
def update_user_progress(sender, instance, **kwargs):
    user_id = instance.user.id
    course_id = instance.assessment.course.id
    total, attempts = calculate(user_id, course_id)

    percent = round(attempts / total * 100, 2) if total > 0 else 0
    
    progress, _ = UserProgress.objects.get_or_create(
        user=instance.user,
        course=instance.assessment.course
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
    else:  # Sự kiện post_delete
        user_id = instance.student.id
        course_id = instance.course.id
        UserProgress.objects.filter(user=instance.student, course=instance.course).delete()
#########################################################################################################
class PerformanceAnalytics(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    average_score = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)

    def update_performance(self):
        highest_score = StudentAssessmentAttempt.objects.filter(
            user=self.user, assessment=OuterRef('assessment')
        ).values('assessment').annotate(highest_score=Max('score_ass')).values('highest_score')

        highest_attempts = StudentAssessmentAttempt.objects.filter(
            user=self.user,
            assessment__course=self.course,
            score_ass__in=Subquery(highest_score)
        )
        
        total_assessments = Assessment.objects.filter(course=self.course).count()
        if total_assessments > 0:
            completed_assessments = highest_attempts.filter().count()
            # print('count:',completed_assessments)
            total_score = highest_attempts.aggregate(models.Sum('score_ass'))['score_ass__sum'] or 0
            self.average_score = round(total_score / completed_assessments, 3) if completed_assessments > 0 else 0
            self.completion_rate = round((completed_assessments / total_assessments) * 100, 2)
        else:
            self.average_score = 0.0
            self.completion_rate = 0.0
        self.save()
    
    class Meta:
        db_table = 'achievement_performance' 

@receiver(post_save, sender=StudentAssessmentAttempt)
@receiver(post_delete, sender=StudentAssessmentAttempt)
def update_performance_analytics(sender, instance, **kwargs):
    try:
        performance = PerformanceAnalytics.objects.get(
            user=instance.user,
            course=instance.assessment.course 
        )
        performance.update_performance()
    except PerformanceAnalytics.DoesNotExist:
        pass



@receiver(post_save, sender=Assessment)
@receiver(post_delete, sender=Assessment)
def update_performance_analytics(sender, instance, **kwargs):
        students = User.objects.filter(id__in=StudentAssessmentAttempt.objects.filter(assessment__course=instance.course).values('user'))
        for student in students:
            performance = PerformanceAnalytics.objects.get(
                user=student,
                course=instance.course
            )
            performance.update_performance()


@receiver(post_save, sender=Enrollment)
def create_performance(sender, instance, created, **kwargs):
    if created:
        PerformanceAnalytics.objects.create(
            user=instance.student,
            course=instance.course
        )

@receiver(post_delete, sender=Enrollment)
def delete_performance(sender, instance, **kwargs):
    try:
        performance = PerformanceAnalytics.objects.get(
            user=instance.student,
            course=instance.course
        )
        performance.delete()
    except PerformanceAnalytics.DoesNotExist:
        pass
#########################################################################################################
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