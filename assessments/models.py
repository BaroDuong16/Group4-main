from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from course.models import Course
from exercises.models import Exercise
from quiz.models import Question, AnswerOption
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

    
class AssessmentType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Assessment Type"
        verbose_name_plural = "Assessment Types"

    def __str__(self):
        return self.type_name
    def save(self, *args, **kwargs):
        # Check for duplicates
        if AssessmentType.objects.filter(type_name=self.type_name).exists():
            raise ValidationError(_("This assessment type already exists."))
        super().save(*args, **kwargs)


class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # This line ensures a course reference
    
    title = models.CharField(max_length=255)
    
    # Many-to-many relationships
    exercises = models.ManyToManyField(Exercise, related_name='assessment', blank=True)
    questions = models.ManyToManyField(Question, related_name='assessment', blank=True)

    # Foreign key to AssessmentType
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name='assessment')

    invited_count = models.IntegerField(default=0, verbose_name="Invited Count")
    assessed_count = models.IntegerField(default=0, verbose_name="Assessed Count")
    qualified_count = models.IntegerField(default=0, verbose_name="Qualified Count") 

    qualify_score = models.IntegerField(default=60, verbose_name="Qualify Score")
    total_score = models.IntegerField(default=100, verbose_name="Total Score")

    quiz_score_ratio  = models.IntegerField(default=40, verbose_name="Quiz score ratio")
    exercise_score_ratio  = models.IntegerField(default=60, verbose_name="Exercise score ratio")
    
    created_at = models.DateTimeField(default=timezone.now)
    # due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments')

    time_limit = models.IntegerField(default=30)
    invited_emails = models.TextField(blank=True, verbose_name="Invited Candidates")
    
    class Meta:
        ordering = ['created_at', 'course']
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"

    def __str__(self):
        return f"{self.title} ({self.assessment_type})"

    def is_past_due(self):
        """Check if the due date has passed."""
        return self.due_date and timezone.now() > self.due_date

    def invite_candidates(self):
        """Send invitations to all invited candidates."""
        candidates = self.invited_candidates.split(',')
        for email in candidates:
            email = email.strip()
            if email:  # Check if email is not empty
                send_mail(
                    'You are Invited to an Assessment',
                    f'You have been invited to participate in the assessment: {self.title}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

class InvitedCandidate(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='invited_candidates_list')
    email = models.EmailField()
    invitation_date = models.DateTimeField(auto_now_add=True)  # Automatically set when the candidate is invited
    expiration_date = models.DateTimeField(null=True, blank=True)  # Can be null until set

    def save(self, *args, **kwargs):
        # Call set_expiration_date before saving the instance
        self.set_expiration_date()
        super().save(*args, **kwargs)

    def set_expiration_date(self, days=7):
        """
        Set the expiration date based on the invitation date and number of days.
        Default is 7 days.
        """
        if self.invitation_date:
            self.expiration_date = self.invitation_date + timedelta(days=days)
        else:
            self.expiration_date = timezone.now() + timedelta(days=days)

    def __str__(self):
        return f"Invited Candidate: {self.email} for {self.assessment.title}"


class StudentAssessmentAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")  # Optional email for anonymous users
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    # Scoring and feedback
    score_quiz = models.IntegerField(default=0, verbose_name="Quiz Score")
    score_ass = models.IntegerField(default=0, verbose_name="Assignment Score")
    note = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Additional fields to track user answers and submissions
    # user_answers = models.ForeignKey(UserAnswer, related_name='attempts', blank=True)
    # user_submissions = models.ManyToManyField('exercises.Submission', related_name='attempts', blank=True)
    is_submitted = models.BooleanField(default=False)
    is_proctored = models.BooleanField(default=False)
    proctoring_data = models.JSONField(null=True, default=dict)
    
    # Timestamps and User relations
    attempt_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Assignment Attempt"
        verbose_name_plural = "Student Assignment Attempts"

    def __str__(self):
        user_info = self.user.username if self.user else self.email  # Display user or email
        return f"Attempt by {user_info} for {self.assessment}"

    def clean(self):
        # Ensure both scores are non-negative
        if self.score_quiz < 0:
            raise ValidationError({'score_quiz': _("Quiz score cannot be negative.")})
        if self.score_ass < 0:
            raise ValidationError({'score_ass': _("Assignment score cannot be negative.")})
        if not self.user and not self.email:
            raise ValidationError(_('Either user or email must be provided.'))

    def save(self, *args, **kwargs):
        # Clean data before saving
        self.clean()
        super().save(*args, **kwargs)


class UserAnswer(models.Model):
    # assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # selected_option = models.ForeignKey(AnswerOption, on_delete=models.SET_NULL, null=True, blank=True)
    selected_options = models.ManyToManyField(AnswerOption, blank=True)
    text_response = models.TextField(null=True, blank=True)
    attempt = models.ForeignKey(StudentAssessmentAttempt, on_delete=models.CASCADE, related_name='quiz_answers')
    def __str__(self):
        return f"Answer for {self.question} in {self.attempt}"