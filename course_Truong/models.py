from django.db import models
from unidecode import unidecode
from user.models import User
import os

class NewCourse(models.Model):
    course_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, max_length=500)
    image = models.ImageField(upload_to='images/')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        try:
            self.image.delete()
        except PermissionError:
            print('Error!')

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.image:
            name, ext = os.path.splitext(self.image.name)
            new_filename = f"{unidecode(name)}{ext}"
            self.image.name = new_filename

        super().save(*args, **kwargs)

    def url(self):
        course_url = unidecode(self.course_name)
        course_url = course_url.lower()
        course_url = course_url.replace(' ', '-')
        return course_url

    def __str__(self):
        return self.course_name


class Sub_Course(models.Model):
    title = models.CharField(max_length=255)
    order = models.IntegerField()
    course = models.ForeignKey(NewCourse, on_delete=models.CASCADE, related_name='sub_courses')

    class Meta:
        unique_together = ('course', 'order')

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=255)
    order = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="course_modules_created")
    sub_course = models.ForeignKey(Sub_Course, on_delete=models.CASCADE, related_name='modules')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'sub_course')

    def __str__(self):
        return self.title


class Sub_Module(models.Model):
    title = models.CharField(max_length=255)
    html_content = models.TextField(blank=True, null=True)
    video_url = models.TextField(blank=True, null=True)
    order = models.IntegerField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sub_modules')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'module')

    def __str__(self):
        return self.title


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    course = models.ForeignKey(NewCourse, on_delete=models.CASCADE, related_name="images")

    def delete(self, *args, **kwargs):
        try:
            self.image.delete()
        except PermissionError:
            print('Error!')

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.image:
            name, ext = os.path.splitext(self.image.name)
            new_filename = f"{unidecode(name)}{ext}"
            self.image.name = new_filename

        super().save(*args, **kwargs)


class Enrolled_Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(NewCourse, on_delete=models.CASCADE, related_name='enrolled_users')

    class Meta:
        unique_together = ('user', 'course')


class Quiz(models.Model):
    quiz_title = models.CharField(max_length=255)
    quiz_description = models.TextField(blank=True, null=True, max_length=500)
    total_mark = models.IntegerField()
    mark_to_pass = models.IntegerField()
    order = models.IntegerField()

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="quizzes_created")
    sub_course = models.ForeignKey(Sub_Course, on_delete=models.CASCADE, related_name='quizzes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'sub_course')

    def __str__(self):
        return self.quiz_title


class Question(models.Model):
    question_text = models.TextField()
    question_type = models.CharField(max_length=50)
    points = models.IntegerField()

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")


class Answer_Option(models.Model):
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')


class Student_Quiz_Attempt(models.Model):
    score = models.FloatField(default=0)
    is_proctored = models.BooleanField(default=False)
    proctoring_data = models.JSONField(null=True)

    attempt_date = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='student_attempts')


class Student_Answer(models.Model):
    attempt = models.ForeignKey(Student_Quiz_Attempt, on_delete=models.CASCADE, related_name="student_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="student_answers")
    selected_option = models.ForeignKey(Answer_Option, on_delete=models.CASCADE, related_name='student_selections')


class AI_Grading(models.Model):
    feedback_text = models.TextField()
    awarded_points = models.IntegerField(default=0)

    answer = models.ForeignKey(Student_Answer, on_delete=models.CASCADE, related_name="ai_gradings")
