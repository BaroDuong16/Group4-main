from django.db import models
from django.contrib.auth.models import User  # Assuming you use the default User model for instructors and students
from course.models import Course
from django.conf import settings

# Model for Quiz
class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quiz_title = models.CharField(max_length=255)
    quiz_description = models.TextField(blank=True, null=True)
    total_marks = models.IntegerField()
    time_limit = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    start_datetime = models.DateTimeField(null=True, blank=True)  
    end_datetime = models.DateTimeField(null=True, blank=True)    
    attempts_allowed = models.PositiveIntegerField(default=1)    


    def __str__(self):
        return self.quiz_title

# Model for Question
class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('TEXT', 'Text Response'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default='MCQ')
    points = models.IntegerField()

    def __str__(self):
        return self.question_text

# Model for Answer Option
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

# Model for Student Quiz Attempt
class StudentQuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    attempt_date = models.DateTimeField(auto_now_add=True)
    is_proctored = models.BooleanField(default=False)
    proctoring_data = models.JSONField(null=True, blank=True)

# Model for Student Answer
class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentQuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(AnswerOption, blank=True) 
    text_response = models.TextField(null=True, blank=True)

# Model for AI Grading
class AIGrading(models.Model):
    answer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    awarded_points = models.IntegerField()
