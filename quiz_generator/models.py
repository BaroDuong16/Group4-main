from django.db import models

class Question(models.Model):
    text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class QuizBank(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    similarity_score = models.FloatField(default=0.0)
    is_added = models.BooleanField(default=False)
